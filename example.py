from droneapi import connect
from droneapi.lib import VehicleMode, Location
from pymavlink import mavutil
from Queue import Queue
from flask import Flask, render_template, jsonify, Response, request
import time
import json

def sse_encode(obj, id=None):
    return "data: %s\n\n" % json.dumps(obj)

# Connect to UDP endpoint
print 'connecting...'
vehicle = connect('udpout:10.1.1.10:14560')
print 'connected to drone.'


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
    """
    Send MAV_CMD_CONDITION_YAW message to point vehicle at a specified heading (in degrees).
    This method sets an absolute heading by default, but you can set the `relative` parameter
    to `True` to set yaw relative to the current yaw heading.
    
    By default the yaw of the vehicle will follow the direction of travel. After setting 
    the yaw using this function there is no way to return to the default yaw "follow direction 
    of travel" behaviour (https://github.com/diydrones/ardupilot/issues/2427)
    
    For more information see: 
    http://copter.ardupilot.com/wiki/common-mavlink-mission-command-messages-mav_cmd/#mav_cmd_condition_yaw
    """
    if relative:
        is_relative=1 #yaw relative to direction of travel
    else:
        is_relative=0 #yaw is an absolute angle
    
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
            is_relative, # param 4, relative offset 1, absolute angle 0
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

@app.route("/api/photo", methods=['POST'])
def api_photo():
    set_gimbal_manual(0, -90, 0)
    condition_yaw(0)
    time.sleep(DURATION)
    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(threaded=True)
