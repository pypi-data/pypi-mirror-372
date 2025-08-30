import asyncio
import pybotters


class Heartbeat:
    @staticmethod
    async def ourbit(ws: pybotters.ws.ClientWebSocketResponse):
        while not ws.closed:
            await ws.send_str('{"method":"ping"}')
            await asyncio.sleep(10.0)

pybotters.ws.HeartbeatHosts.items['futures.ourbit.com'] = Heartbeat.ourbit