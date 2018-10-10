import requests

from flask import Flask, Response, jsonify, render_template
from flask import request as flask_request

from flask_cors import CORS
import os

from ddtrace import tracer, patch, config
from ddtrace.contrib.flask import TraceMiddleware

import subprocess
import random

# Tracer configuration
tracer.configure(hostname='agent')
tracer.set_tags({'env': 'workshop'})
patch(requests=True)

# enable distributed tracing for requests
# to send headers (globally)
config.requests['distributed_tracing'] = True

app = Flask('api')

if os.environ['FLASK_DEBUG']:
    CORS(app)

traced_app = TraceMiddleware(app, tracer, service='iot-frontend')

@app.route('/')
def homepage():
    return app.send_static_file('index.html')

@app.route('/service-worker.js')
def service_worker_js():
    return app.send_static_file('js/service-worker.js')

@app.route('/status')
def system_status():
    status = requests.get('http://sensors:5002/sensors').json()
    app.logger.info(f"Sensor status: {status}")
    pumps = requests.get('http://pumps:5001/devices').json()
    users = requests.get('http://noder:5004/users').json()
    return jsonify({'sensor_status': status, 'pump_status': pumps, 'users': users})

@app.route('/users', methods=['GET', 'POST'])
def users():
    if flask_request.method == 'POST':
        newUser = flask_request.get_json()
        userStatus = requests.post('http://noder:5004/users', json=newUser).json()
        return jsonify(userStatus)
    elif flask_request.method == 'GET':
        users = requests.get('http://noder:5004/users').json()
        return jsonify(users)

@app.route('/add_sensor')
def add_sensor():
    sensors = requests.post('http://sensors:5002/sensors').json()
    return jsonify(sensors)
    
@app.route('/add_pump', methods=['POST'])
def add_pump():
    pumps = requests.post('http://pumps:5001/devices').json()
    app.logger.info(f"Adding {pumps} to the pumps pool")
    return jsonify(pumps)

@app.route('/generate_requests', methods=['POST'])
def call_generate_requests():
    payload = flask_request.get_json()
    span = tracer.current_span()
    app.logger.info(f"Looking at {span}")
    app.logger.info(f"with span id {span.span_id}")
    span = tracer.current_span()

    span.set_tags({'requests': payload['total'], 'concurrent': payload['concurrent']})

    output = subprocess.check_output(['/app/traffic_generator.py',
                                      str(payload['concurrent']), 
                                      str(payload['total']),
                                      str(payload['url'])])
    app.logger.info(f"Result for subprocess call: {output}")
    return jsonify({'traffic': str(payload['concurrent']) + ' concurrent requests generated, ' + 
                               str(payload['total'])  + ' requests total.',
                    'url': payload['url']})

# generate requests for one user to see tagged
@app.route('/generate_requests_user')
def call_generate_requests_user():
    users = requests.get('http://noder:5004/users').json()
    user = random.choice(users)
    span = tracer.current_span()
    span.set_tags({'current_user': user['uid']})
    output = subprocess.check_output(['/app/traffic_generator.py',
                                     '20',
                                     '100',
                                     'http://noder:5004/users/' + user['uid']])
    app.logger.info(f"Chose random user {user['name']} for requests: {output}")
    return jsonify({'random_user': user['name']})

@app.route('/simulate_sensors')
def simulate_sensors():
    sensors = requests.get('http://sensors:5002/refresh_sensors').json()
    return jsonify(sensors)