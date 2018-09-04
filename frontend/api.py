import requests

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

app = Flask('api')
traced_app = TraceMiddleware(app, tracer, service='thinker-api')

@app.route('/')
def hello():
    return Response({'Hello from the API': 'world'}, mimetype='application/json')

@app.route('/status')
def status():
    status = requests.get('http://sensors:5002/get_sensors').json()
    lights = requests.get('http://internetthing:5001/get_devices').json()
    return jsonify({'sensor_status': status, 'pump_status': lights})