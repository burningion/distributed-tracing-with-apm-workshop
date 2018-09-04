import requests
from  openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption

from flask import Flask, Response, jsonify
from flask import request as flask_request

from ddtrace import tracer, patch, config
from ddtrace.contrib.flask import TraceMiddleware


# Tracer configuration
tracer.configure(hostname='agent')
patch(requests=True)

# enable distributed tracing for requests
# to send headers (globally)
config.requests['distributed_tracing'] = True

app = Flask('thing')
traced_app = TraceMiddleware(app, tracer, service='edge-thing')

iot_devices = [{'pump_no': 1, 'status': 'OFF'},
                {'pump_no': 2, 'status': 'OFF'},
                {'pump_no': 3, 'status': 'OFF'}]

@app.route('/')
def hello():
    return Response({'Hello from IoT Device': 'world'}, mimetype='application/json')

@app.route('/get_devices')
def status():
    return jsonify({'pump_count': len(iot_devices),
                    'status': iot_devices})