#!/bin/bash

SERVER_SCRIPT="/app/Python/Server.py"
CLIENT_SCRIPT="/app/Python/Client.py"

cleanup() {
    echo "Oprire server (PID $SERVER_PID)..."
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    echo "Server oprit."
}
trap cleanup EXIT INT TERM

echo "Pornesc serverul..."
python3 $SERVER_SCRIPT &
SERVER_PID=$!

echo "Astept serverul sa fie gata..."
sleep 1

echo "Pornesc clientul..."
python3 $CLIENT_SCRIPT