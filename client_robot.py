import asyncio
import websockets
import json
import time

from client_utils import *
from constants import *


server_ip = SERVER_IP

async def send_data(uri, dataset_path):
    async with websockets.connect(uri) as websocket:
        dataset = get_data(dataset_path)
        for data in dataset:
            request = make_request(data)

            await websocket.send(request)

            response = await websocket.recv()
            actuate_response(response)


async def main():
    print("Sending data")
    uri = f"ws://{server_ip}:8765"
    dataset_path = "dataset"

    await send_data(uri, dataset_path)

asyncio.run(main())
