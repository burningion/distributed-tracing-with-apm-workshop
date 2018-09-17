#!/usr/local/bin/python
from requests_threads import AsyncSession
import asyncio
import argparse

from ddtrace import tracer, patch, config

tracer.configure(hostname='agent')
tracer.set_tags({'env': 'dev'})
patch(requests=True)

# enable distributed tracing for requests
# to send headers (globally)
config.requests['distributed_tracing'] = True

parser = argparse.ArgumentParser(description='Concurrent Traffic Generator')
parser.add_argument('concurrent', type=int, help='Number of Concurrent Requests')
parser.add_argument('total', type=int, help='Total number of Requests to Make')
parser.add_argument('url', type=str, help='URL to fetch')
parser.add_argument('parent_id', type=int, help='Parent id of trace')
parser.add_argument('trace_id', type=int, help='Trace id of requests')
args = parser.parse_args()

asyncio.set_event_loop(asyncio.new_event_loop())

session = AsyncSession(n=args.concurrent)

span = tracer.trace('Requests Shell Call')
span.trace_id = args.trace_id
if args.parent_id != 0:
    span.parent_id = args.parent_id

async def generate_requests():
    rs = []
    for _ in range(args.total):
        rs.append(session.get(args.url))
    for i in range(args.total):
        rs[i] = await rs[i]
    print(rs)

session.run(generate_requests)
span.finish()