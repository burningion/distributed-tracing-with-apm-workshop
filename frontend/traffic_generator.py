#!/usr/local/bin/python
from requests_threads import AsyncSession
import asyncio
import argparse

parser = argparse.ArgumentParser(description='Concurrent Traffic Generator')
parser.add_argument('concurrent', type=int, help='Number of Concurrent Requests')
parser.add_argument('total', type=int, help='Total number of Requests to Make')
args = parser.parse_args()

asyncio.set_event_loop(asyncio.new_event_loop())

session = AsyncSession(n=args.concurrent)

async def generate_requests():
    rs = []
    for _ in range(args.total):
        rs.append(session.get('http://noder:5004/users'))
    for i in range(args.total):
        rs[i] = await rs[i]
    print(rs)

session.run(generate_requests)