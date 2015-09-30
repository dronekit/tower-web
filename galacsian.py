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
import sys
import socket
from threading import Thread
from subprocess import Popen
from flask import render_template
from flask import Flask, Response

vehicle = None

# Allow us to reuse sockets after the are bound.
# http://stackoverflow.com/questions/25535975/release-python-flask-port-when-script-is-terminated
socket.socket._bind = socket.socket.bind
def my_socket_bind(self, *args, **kwargs):
    self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return socket.socket._bind(self, *args, **kwargs)
socket.socket.bind = my_socket_bind

def sse_encode(obj, id=None):
    return "data: %s\n\n" % json.dumps(obj)

def state_msg():
    if vehicle.location.lat == None:
        raise Exception('no position info')
    if vehicle.armed == None:
        raise Exception('no armed info')
    return {"armed": vehicle.armed, "alt": vehicle.location.alt, "mode": vehicle.mode.name, "lat": vehicle.location.lat, "lon": vehicle.location.lon}

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

listeners_location = []
listeners_location

from threading import Thread
import time
def tcount():
    while True:
        time.sleep(0.25)
        try:
            msg = state_msg()
            for x in listeners_location:
                x.put(msg)
        except Exception as e:
            pass
t = Thread(target=tcount)
t.daemon = True
t.start()

@app.route("/api/sse/state")
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

# @app.route("/api/location", methods=['GET', 'POST', 'PUT'])
# def api_location():
#     if request.method == 'POST' or request.method == 'PUT':
#         try:
#             data = request.get_json()
#             (lat, lon) = (float(data['lat']), float(data['lon']))
#             goto(lat, lon)
#             return jsonify(ok=True)
#         except Exception as e:
#             print(e)
#             return jsonify(ok=False)
#     else:
#         return jsonify(**location_msg())


@app.route("/api/arm", methods=['POST', 'PUT'])
def api_location():
    if request.method == 'POST' or request.method == 'PUT':
        try:
            vehicle.armed = True
            vehicle.flush()
            return jsonify(ok=True)
        except Exception as e:
            print(e)
            return jsonify(ok=False)

def connect_to_drone():
    global vehicle

    print 'connecting to drone...'
    while not vehicle:
        try:
            vehicle = connect(sys.argv[1])
        except Exception as e:
            print 'waiting for connection...'
            time.sleep(2)
    print 'connected!'

t2 = Thread(target=connect_to_drone)
t2.daemon = True
t2.start()

if __name__ == "__main__":
    app.run(threaded=True, host='0.0.0.0', port=24403)
