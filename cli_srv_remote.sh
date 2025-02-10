#!/bin/bash

server_path="path/to/server.py"
server_env_name="robot"

client_ip="client@ip"
client_path="path/to/client.py"
client_env_name="piper"

ssh client_ip "conda activate ${client_env_name}&&python client_path"

conda activate ${server_env_name}
python ${server_path}