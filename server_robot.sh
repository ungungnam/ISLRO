#!/bin/bash

remote_env_name="robot"
server_python_path="server_robot.py"

source ~/.bashrc
export PATH=~/miniconda3/bin:$PATH
conda run -n ${remote_env_name} python ${server_python_path}
