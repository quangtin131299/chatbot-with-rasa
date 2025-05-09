#!/bin/sh

echo "Starting Rasa Action Server on port 5055..."
exec rasa run actions &

echo "Starting Rasa Server on port ${RASA_PORT:-5005} with API enabled..."
exec rasa run -m rasa_model.tar.gz --enable-api --cors "*" --debug
