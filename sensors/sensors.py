import requests

from flask import Flask, Response, jsonify
from flask import request as flask_request

from ddtrace import tracer, patch, config
from ddtrace.contrib.flask import TraceMiddleware

import random

sensors = []

# Tracer configuration
tracer.configure(hostname='agent')
patch(requests=True)

# enable distributed tracing for requests
# to send headers (globally)
config.requests['distributed_tracing'] = True

app = Flask('sensors')
traced_app = TraceMiddleware(app, tracer, service='edge-thing')

@app.route('/')
def hello():
    return Response({'Hello from Sensors': 'world'}, mimetype='application/json')

# forget REST for now
@app.route('/add_sensor')
def add_sensor():
    sensors.append({'sensor_no': len(sensors) + 1, 'value': random.randint(1,100)})
    return jsonify(sensors)

@app.route('/get_sensors')
def get_sensors():
    return jsonify({'sensor_count': len(sensors),
                    'system_status': sensors})