import asyncio
import websockets
import json
import time

from client_utils import *
from constants import *


server_ip = SERVER_IP

async def read_obs():
    obs = read_camera()
    return obs


async def send_obs(obs, websocket):
    await websocket.send(obs)
    actions = await websocket.recv()

    return actions


async def actuate(actions):
    command_robot(actions)


async def main():
    print("client opened")
    uri = f"ws://{server_ip}:8765"

    obs = None
    actions = None

    async with websockets.connect(uri) as websocket:
        while True:
            read_obs_task = asyncio.create_task(read_obs())
            send_obs_task = asyncio.create_task(send_obs(obs, websocket))
            actuate_task = asyncio.create_task(actuate(actions))

            await read_obs_task
            await send_obs_task
            await actuate_task

            obs = read_obs_task.result()
            actions = send_obs_task.result()

asyncio.run(main())
