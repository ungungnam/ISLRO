import sys
import json
import time

def temp(data):
    #time.sleep(0.1)
    return {"action" : ["joint_data", "end_pointer_data"]}

if __name__ == "__main__":
    print(sys.argv)
    input_data = json.loads(sys.argv[1])
    result = temp(input_data)

    print(json.dumps(result)) # server.py reads result(action) by stdout