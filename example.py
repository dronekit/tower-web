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

def sse_encode(obj, id=None):
    return "data: %s\n\n" % json.dumps(obj)

def location_msg():
    try:
        return {"lat": vehicle.location.lat, "lon": vehicle.location.lon}
    except:
        return {"lat": 0, "lon": 0}

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

if __name__ == "__main__":
    # Connect to UDP endpoint
    print 'connecting...'
    vehicle = connect('udpout:127.0.0.1:14550')
    print 'connected to drone.'
    app.run(threaded=True, host='0.0.0.0')
