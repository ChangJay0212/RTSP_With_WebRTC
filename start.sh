#!/bin/bash

# start Docker Compose
docker compose up -d 

# service warm-up time
sleep 5

# auto open web
xdg-open http://localhost:8003/index.html
