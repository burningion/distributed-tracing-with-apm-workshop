import requests

from flask import Flask, Response, jsonify, render_template
from flask import request as flask_request

from flask_cors import CORS
import os

from ddtrace import tracer, patch, config
from ddtrace.contrib.flask import TraceMiddleware

import subprocess

# Tracer configuration
tracer.configure(hostname='agent')
tracer.set_tags({'env': 'dev'})
patch(requests=True)

# enable distributed tracing for requests
# to send headers (globally)
config.requests['distributed_tracing'] = True

app = Flask('api')

if os.environ['FLASK_DEBUG']:
    CORS(app)

traced_app = TraceMiddleware(app, tracer, service='iot-frontend')

@app.route('/')
def hello():
    sensors = requests.get('http://sensors:5002/sensors').json()
    return render_template('index.html', sensors=sensors)

@app.route('/status')
def status():
    status = requests.get('http://sensors:5002/sensors').json()
    lights = requests.get('http://internetthing:5001/devices').json()
    users = requests.get('http://noder:5004/users').json()
    return jsonify({'sensor_status': status, 'pump_status': lights, 'users': users})

@app.route('/add_sensor')
def add_sensor():
    sensors = requests.post('http://sensors:5002/sensors').json()
    return jsonify({'sensors': sensors})
    
@app.route('/generate_requests', methods=['POST'])
def call_generate_requests():
    payload = flask_request.get_json()
    subprocess.check_output(['/app/traffic_generator.py',
                             str(payload['concurrent']), 
                             str(payload['total']),
                             str(payload['url'])])

    return jsonify({'traffic': str(payload['concurrent']) + ' concurrent requests generated, ' + 
                               str(payload['total'])  + ' requests total.',
                    'url': payload['url']})