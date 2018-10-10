#!/usr/local/bin/python
from ddtrace import tracer, patch, config, Pin
tracer.configure(hostname='agent')
patch(requests=True,futures=True,asyncio=True)

tracer.set_tags({'env': 'workshop'})
tracer.debug_logging = True

import asyncio
import argparse
from requests_threads import AsyncSession
# enable distributed tracing for requests
# to send headers (globally)

import logging
logger = logging.getLogger()
config.requests['distributed_tracing'] = True

parser = argparse.ArgumentParser(description='Concurrent Traffic Generator')
parser.add_argument('concurrent', type=int, help='Number of Concurrent Requests')
parser.add_argument('total', type=int, help='Total number of Requests to Make')
parser.add_argument('url', type=str, help='URL to fetch')
args = parser.parse_args()

asyncio.set_event_loop(asyncio.new_event_loop())

session = AsyncSession(n=args.concurrent)
Pin.override(session, service='concurrent-requests-generator')

async def generate_requests():
    with tracer.trace('flask.request', service='concurrent-requests-generator') as span:
        rs = []
        for _ in range(args.total):
            rs.append(session.get(args.url))
        for i in range(args.total):
            rs[i] = await rs[i]
        print(rs)

session.run(generate_requests)
session.close()