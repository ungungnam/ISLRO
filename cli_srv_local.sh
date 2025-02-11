#!/bin/bash

server_ip="mjbae@147.47.239.153"
ws_path="~/codes/islab_ws/ISLRO"
server_file_path="server_robot.sh"

client_path="path/to/client.py"
local_env_name="piper"

ssh ${server_ip} "source ~/.bashrc && cd ${ws_path} && source ${server_file_path}"

conda activate ${local_env_name}
python ${client_path}
