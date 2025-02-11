import asyncio
import websockets
import json
import time

from temp import *


while True:
    print("starting client...")
    time.sleep(20)

async def send_data():
    print("Sending data")
    uri = "ws://localhost:8765"

    async with websockets.connect(uri) as websocket:
        # 예제 입력 데이터 (사용자가 원하는 방식으로 생성 가능)
        input_data = {"sensor1": 10.5, "sensor2": 22.3, "sensor3": 5.1}
        print(f"📤 Sending data: {input_data}")

        await websocket.send(json.dumps(input_data))  # JSON 형식으로 데이터 전송

        response = await websocket.recv()  # 응답 수신
        action = json.loads(response)["action"]
        print(f"📥 Received action: {action}")

        temp(action)  # actuate

asyncio.run(send_data())
