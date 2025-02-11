#!/bin/bash

server_ip="mjbae@147.47.239.153"
ws_path="~/codes/islab_ws/ISLRO"
server_file_path="server_robot.sh"

client_path="client_robot.py"
local_env_name="piper"

ssh ${server_ip} "cd ${ws_path} && source ${server_file_path}" &
conda run -n ${local_env_name} python ${client_path}
