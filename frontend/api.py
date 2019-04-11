import requests

from flask import Flask, Response, jsonify, render_template
from flask import request as flask_request

from flask_cors import CORS
import os

from ddtrace import tracer
from ddtrace.ext.priority import USER_REJECT, USER_KEEP


import subprocess
import random

app = Flask('api')

if os.environ['FLASK_DEBUG']:
    CORS(app)

@app.route('/')
def homepage():
    app.logger.info("Homepage called")
    return app.send_static_file('index.html')

@app.route('/service-worker.js')
def service_worker_js():
    app.logger.info("Service worker JS called")
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
        app.logger.info(f"Adding new user: {newUser}")
        userStatus = requests.post('http://noder:5004/users', json=newUser).json()
        return jsonify(userStatus)
    elif flask_request.method == 'GET':
        app.logger.info(f"Getting all users")
        users = requests.get('http://noder:5004/users').json()
        return jsonify(users)

@app.route('/add_sensor')
def add_sensor():
    app.logger.info('Adding a new sensor')
    sensors = requests.post('http://sensors:5002/sensors').json()
    return jsonify(sensors)
    
@app.route('/add_pump', methods=['POST'])
def add_pump():
    pumps = requests.post('http://pumps:5001/devices').json()
    app.logger.info(f"Getting {pumps}")
    return jsonify(pumps)

@app.route('/generate_requests', methods=['POST'])
def call_generate_requests():
    payload = flask_request.get_json()
    span = tracer.current_root_span()
    span.context.sampling_priority = USER_KEEP
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
# enable user sampling because low request count
@app.route('/generate_requests_user')
def call_generate_requests_user():
    users = requests.get('http://noder:5004/users').json()
    user = random.choice(users)
    span = tracer.current_root_span()
    span.context.sampling_priority = USER_KEEP
    span.set_tags({'user_id': user['id']})

    output = subprocess.check_output(['/app/traffic_generator.py',
                                     '20',
                                     '100',
                                     'http://noder:5004/users/' + user['uid']])
    app.logger.info(f"Chose random user {user['name']} for requests: {output}")
    return jsonify({'random_user': user['name']})

@app.route('/simulate_sensors')
def simulate_sensors():
    app.logger.info('Simulating refresh of sensor data')
    sensors = requests.get('http://sensors:5002/refresh_sensors').json()
    return jsonify(sensors)