import requests
from  openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption

from flask import Flask, Response, jsonify
from flask import request as flask_request

from ddtrace import tracer, patch, config
from ddtrace.contrib.flask import TraceMiddleware
import random

# Tracer configuration
tracer.configure(hostname='agent')
tracer.set_tags({'env': 'dev'})
patch(requests=True)

# enable distributed tracing for requests
# to send headers (globally)
config.requests['distributed_tracing'] = True

app = Flask('thing')
traced_app = TraceMiddleware(app, tracer, service='pumps-service', distributed_tracing=True)

iot_devices = [{'id': 1, 'name': 'Pump 1', 'status': 'OFF', 'gph': 5.10},
                {'id': 2, 'name': 'Pump 2', 'status': 'OFF', 'gph': 3002.10},
                {'id': 3, 'name': 'Pump 3', 'status': 'ON', 'gph': 5242.10},]

@app.route('/')
def hello():
    return Response({'Hello from Oxygenation Pumps': 'world'}, mimetype='application/json')

@app.route('/devices', methods=['GET', 'POST'])
def status():
    global iot_devices
    if flask_request.method == 'GET':
        return jsonify({'pump_count': len(iot_devices),
                        'status': iot_devices})
    elif flask_request.method == 'POST':
        # create a new device w/ random status
        iot_devices.append({'id': len(iot_devices) + 1, 
                            'name': 'Pump ' + str(len(iot_devices) + 1),
                            'status': random.choice(['OFF', 'ON']),
                            'gph': random.randint(10,500)})
        return jsonify(iot_devices)
    else:
        err = jsonify({'error': 'Invalid request method'})
        err.status_code = 405
        return err