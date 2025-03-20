#!/bin/bash

SERVER_SCRIPT="../Python/server.py"
CLIENT_SCRIPT="../Python/client.py"

echo "Pornesc serverul..."
python3 $SERVER_SCRIPT &
SERVER_PID=$!

sleep 1

echo "Pornesc clientul..."
python3 $CLIENT_SCRIPT

echo "Oprire server..."
kill $SERVER_PID
