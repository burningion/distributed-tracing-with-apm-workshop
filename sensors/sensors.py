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

@app.route('/sensors', methods=['GET', 'PUT'])
def get_sensors():
    if flask_request.method == 'GET':
        return jsonify({'sensor_count': len(sensors),
                        'system_status': sensors})
    elif flask_request.method == 'PUT':
        sensors.append({'sensor_no': len(sensors) + 1, 'value': random.randint(1,100)})
        return jsonify(sensors)
    else:
        err = jsonify({'error': 'Invalid request method'})
        err.status_code = 405
        return err

@app.route('/refresh_sensors')
def refresh_sensors():
    for sensor in sensors:
        sensor['value'] = random.randint(1,100)
    return jsonify({'sensor_count': len(sensors),
                    'system_status': sensors})