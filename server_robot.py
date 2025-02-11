import asyncio
import websockets
import json
import time

from temp import *

while True:
    print("starting server...")
    time.sleep(10)

async def handler(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        action = temp(data) # predict action
        await websocket.send(json.dumps({"action": action}))  # 결과 전송

async def main():
    server = await websockets.serve(handler, "localhost", 8765)
    print("✅ WebSocket 서버 시작 (ws://localhost:8765)")
    await server.wait_closed()

asyncio.run(main())
