import asyncio
import websockets
import json
import time

from temp import *
from constants import *
from server_utils import *

server_ip = SERVER_IP

async def handler(websocket, path):
    model_for_inference = model()

    while True:
        async for data in websocket:
            if data == 'hello server':
                await websocket.send("hello client")

            # input = process_data(data)
            # output = model_for_inference(input)
            #
            # await websocket.send(output)


async def main():
    server = await websockets.serve(handler, server_ip, 8765)
    await server.wait_closed()

asyncio.run(main())
