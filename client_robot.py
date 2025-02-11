import asyncio
import websockets
import json
import time

from temp import *


async def main():
    print("Sending data")
    uri = "ws://localhost:8765"

    async with websockets.connect(uri) as websocket:
        dataset = get_data()
        request = make_request(dataset)

        await websocket.send(request)

        response = await websocket.recv()
        actuate(response)

asyncio.run(main())
