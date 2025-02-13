import asyncio
import websockets
import json
import time
import numpy as np

from robot_act import *

print("starting client...")

async def send_data():
    print("Sending data")
    uri = "ws://localhost:8765"

    async with websockets.connect(uri) as websocket:
        record_send_time = []
        for i in range (10):
            t_before = time.time()
            # 예제 입력 데이터 (사용자가 원하는 방식으로 생성 가능) (image + joint)
            input_data = {"sensor1": i, "sensor2": i*2, "sensor3": i*3}

            await websocket.send(json.dumps(input_data))  # JSON 형식으로 데이터 전송
            print(f"1️⃣ Sent data: {input_data}")

            response = await websocket.recv()  # 응답 수신
            action = json.loads(response)["action"]
            print(f"2️⃣ Received action: {action}")

            actuate(action)  # actuate
            print(f"✅ Moving robot arm")

            t_after = time.time()
            record_send_time.append(t_after - t_before)

            await asyncio.sleep(0.3)
        print(f"average sending time : {np.mean(record_send_time)}")

asyncio.run(send_data())
