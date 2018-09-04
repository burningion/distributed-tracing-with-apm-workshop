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

app = Flask('sensors')
traced_app = TraceMiddleware(app, tracer, service='edge-thing')

@app.route('/')
def hello():
    return Response({'Hello from Sensors': 'world'}, mimetype='application/json')
