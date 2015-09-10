#!/usr/bin/env python

from droneapi import connect
from droneapi.lib import VehicleMode, Location
from pymavlink import mavutil
from Queue import Queue
from flask import Flask, render_template, jsonify, Response, request
import time
import json
import urllib
import atexit
import os
import socket
from threading import Thread
from subprocess import Popen
from flask import render_template
from flask import Flask, Response

# Allow us to reuse sockets after the are bound.
# http://stackoverflow.com/questions/25535975/release-python-flask-port-when-script-is-terminated
socket.socket._bind = socket.socket.bind
def my_socket_bind(self, *args, **kwargs):
    self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return socket.socket._bind(self, *args, **kwargs)
socket.socket.bind = my_socket_bind

def launch_mjpegserver():
    """
    Start gstreamer pipeline to launch mjpeg server.
    """
    mjpegserver = Popen(['gst-launch', 'v4l2src', 'device=/dev/video2', '!',
        'jpegenc', '!',
        'tcpserversink', 'port=6000', 'sync=false'])
    def mjpegserver_cleanup():
        mjpegserver.kill()
    atexit.register(mjpegserver_cleanup)

jpg = ''

def mjpegthread():
    global jpg
    while True:
        try:
            stream=urllib.urlopen('http://localhost:6000/')
            bytes=''
            while True:
                bytes += stream.read(1024)
                a = bytes.find('\xff\xd8')
                b = bytes.find('\xff\xd9')
                if a!=-1 and b!=-1:
                    jpg = bytes[a:b+2]
                    bytes= bytes[b+2:]
        except:
            try:
                stream.close()
            except:
                pass

def launch_mjpegclient():
    """
    Launches a client for the mjpeg server that caches one
    jpeg at a time, globally.
    """
    t = Thread(target=mjpegthread)
    t.daemon = True
    t.start()

def sse_encode(obj, id=None):
    return "data: %s\n\n" % json.dumps(obj)

def set_gimbal_manual(roll, pitch, yaw):
    if not (pitch >= -90) or not (pitch <= 0):
        raise Exception('Gimbal angle must be between -90 and 0')

    for i in range(0, 5):
        time.sleep(.1)
        # set gimbal targeting mode
        msg = vehicle.message_factory.mount_configure_encode(
            0, 1,    # target system, target component
            mavutil.mavlink.MAV_MOUNT_MODE_MAVLINK_TARGETING,  #mount_mode
            1,  # stabilize roll
            1,  # stabilize pitch
            1,  # stabilize yaw
            )
        vehicle.send_mavlink(msg)
        vehicle.flush()

    for i in range(0, 5):
        time.sleep(.1)
        msg = vehicle.message_factory.mount_control_encode(
            0, 1,    # target system, target component
            pitch*100.0, # pitch is in centidegrees
            roll*100.0, # roll
            yaw*100.0, # yaw is in centidegrees
            0 # save position
            )
        vehicle.send_mavlink(msg)
        vehicle.flush()

def condition_yaw(heading, relative=False):
    for i in range(0, 5):
        time.sleep(0.1)
        vehicle.mode = VehicleMode("GUIDED")
        # create the CONDITION_YAW command using command_long_encode()
        msg = vehicle.message_factory.command_long_encode(
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
            0, #confirmation
            heading,    # param 1, yaw in degrees
            0,          # param 2, yaw speed deg/s
            1,          # param 3, direction -1 ccw, 1 cw
            1 if relative else 0, # param 4, relative offset 1, absolute angle 0
            0, 0, 0)    # param 5 ~ 7 not used
        # send command to vehicle
        vehicle.send_mavlink(msg)
        vehicle.flush()

DURATION=5

def goto(lat, lon, alt=30):
    print 'GOING TO', (lat, lon)
    for i in range(0, 5):
        time.sleep(.1)
        # Set mode to guided - this is optional as the goto method will change the mode if needed.
        vehicle.mode = VehicleMode("GUIDED")
        # Set the target location and then call flush()
        a_location = Location(lat, lon, alt, is_relative=True)
        vehicle.commands.goto(a_location)
        vehicle.flush()


print 'connecting...'
vehicle = connect('udpout:10.1.1.10:14560')
print 'connected to drone.'

def location_msg():
    return {"lat": vehicle.location.lat, "lon": vehicle.location.lon}

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

listeners_location = []

from threading import Thread
import time
def tcount():
    while True:
        time.sleep(0.25)
        msg = location_msg()
        for x in listeners_location:
            x.put(msg)
t = Thread(target=tcount)
t.daemon = True
t.start()

@app.route("/api/sse/location")
def api_sse_location():
    def gen():
        q = Queue()
        listeners_location.append(q)
        try:
            while True:
                result = q.get()
                ev = sse_encode(result)
                yield ev.encode()
        except GeneratorExit: # Or maybe use flask signals
            listeners_location.remove(q)

    return Response(gen(), mimetype="text/event-stream")

@app.route("/api/location", methods=['GET', 'POST', 'PUT'])
def api_location():
    if request.method == 'POST' or request.method == 'PUT':
        try:
            data = request.get_json()
            (lat, lon) = (float(data['lat']), float(data['lon']))

            
            goto(lat, lon)

            return jsonify(ok=True)
        except Exception as e:
            print(e)
            return jsonify(ok=False)
    else:
        return jsonify(**location_msg())

@app.route("/api/photo", methods=['GET'])
def api_photo():
    try:
        set_gimbal_manual(0, -90, 0)
        condition_yaw(0)
        time.sleep(DURATION)
        return Response(jpg, mimetype='image/jpeg')
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify(ok=False)

if __name__ == "__main__":
    # Connect to UDP endpoint
    if 'LOCAL_TEST' not in os.environ:
        launch_mjpegserver()
        launch_mjpegclient()
    app.run(threaded=True, host='0.0.0.0')
