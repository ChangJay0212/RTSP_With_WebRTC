#!/bin/bash

# start Docker Compose
docker compose -f docker-compose-udp2hls.yml up -d

# service warm-up time
sleep 5

# auto open web
xdg-open ./index.html

