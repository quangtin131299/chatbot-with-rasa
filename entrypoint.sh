#!/bin/sh

echo "Starting Rasa Action Server on port 5055..."
exec rasa run actions &

echo "Starting Rasa Server on port with API enabled..."
exec rasa run -m models/rasa_model.tar.gz --enable-api --cors "*" --debug
