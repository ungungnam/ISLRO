import asyncio
import websockets
import json
import time

from client_utils import *
from constants import *


server_ip = SERVER_IP

async def send_data(uri, dataset_path):
    async with websockets.connect(uri) as websocket:
        # dataset = get_data(dataset_path)
        dataset = "hello server"

        await websocket.send(dataset)
        response = await websocket.recv()
        print(response)


async def main():
    print("Sending data")
    uri = f"ws://{server_ip}:8765"
    dataset_path = "dataset"

    await send_data(uri, dataset_path)

asyncio.run(main())
