import asyncio
import websockets
import json
import time
import subprocess

from temp import *

# while True:
#   print("starting server...")
#   time.sleep(10)
print("starting server...")

async def run_temp(input_data): # running temp.py
    process = await asyncio.create_subprocess_exec( # make new process
        "python", "temp.py", json.dumps(input_data),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, stderr = await process.communicate() # wait until process is finished

    stdout_str = stdout.decode().strip()
    stdout_lines = stdout_str.split("\n")  # 여러 줄 분리
    json_output = stdout_lines[-1].strip()  # 마지막 줄만 가져옴

    if stderr:
        err_msg = stderr.decode().strip()
        print(f"Error in external script: {stderr.decode().strip()}")
        return {"error" : err_msg}

    return json.loads(json_output)



async def handler(websocket, path):
    async for message in websocket:
        data = json.loads(message) # data from client
        print(f"Received data from client: {data}")

        action = await run_temp(data) # wait until action
        #action = temp(data) # predict action at server

        if action is not None:
            await websocket.send(json.dumps({"action": action}))  # 결과 전송
        else:
            await websocket.send(json.dumps({"error": "Processing failed"}))
        print(f"Sent data to client: {action}")


async def main():
    server = await websockets.serve(handler, "localhost", 8765)
    print("✅ WebSocket 서버 시작 (ws://localhost:8765)")
    await server.wait_closed()

asyncio.run(main())
