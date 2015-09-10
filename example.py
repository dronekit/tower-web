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
            print 'GOING TO', (lat, lon)
            # Set mode to guided - this is optional as the goto method will change the mode if needed.
            vehicle.mode = VehicleMode("GUIDED")
            # Set the target location and then call flush()
            a_location = Location(lat, lon, 30, is_relative=True)
            vehicle.commands.goto(a_location)
            vehicle.flush()

            return jsonify(ok=True)
        except Exception as e:
            print(e)
            return jsonify(ok=False)
    else:
        return jsonify(**location_msg())

if __name__ == "__main__":
    app.run(threaded=True)
