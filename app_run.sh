#!/bin/bash

CONTAINER="python_movie_app"

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "Pornesc containerul..."
    docker compose up -d
    sleep 2
fi

echo "Rulez aplicatia in container..."
docker exec -it $CONTAINER bash /app/scripts/start.sh