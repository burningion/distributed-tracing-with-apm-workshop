#!/usr/local/bin/python
from requests_threads import AsyncSession
import asyncio
asyncio.set_event_loop(asyncio.new_event_loop())

session = AsyncSession(n=100)

async def generate_requests():
    rs = []
    for _ in range(10):
        rs.append(session.get('http://noder:5004/users'))
    for i in range(10):
        rs[i] = await rs[i]
    print(rs)

rs = session.run(generate_requests)