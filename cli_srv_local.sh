#!/bin/bash

server_ip="mjbae@147.47.239.153"
server_path="path/to/server.py"
server_env_name="robot"

client_path="path/to/client.py"
client_env_name="piper"

ssh server_ip "conda activate ${server_env_name}&&python server_path"

conda activate ${client_env_name}
python ${client_path}