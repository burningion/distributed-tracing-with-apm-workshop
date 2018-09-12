import requests

from flask import Flask, Response, jsonify, render_template
from flask import request as flask_request

from ddtrace import tracer, patch, config
from ddtrace.contrib.flask import TraceMiddleware


# Tracer configuration
tracer.configure(hostname='agent')
tracer.set_tags({'env': 'dev'})
patch(requests=True)

# enable distributed tracing for requests
# to send headers (globally)
config.requests['distributed_tracing'] = True

app = Flask('api')
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
