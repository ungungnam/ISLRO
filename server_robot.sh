#!/bin/bash

remote_env_name="robot"
server_python_path="server_robot.py"

conda activate ${remote_env_name}
python ${server_python_path}