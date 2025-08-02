#!/bin/bash
sudo apt-get update
sudo apt-get install -y python3-pip

# Copy app files
sudo mkdir -p /app
sudo cp /tmp/main.py /app/
sudo cp /tmp/requirements.txt /app/

# Install dependencies
pip3 install -r /app/requirements.txt

# Run the app with Gunicorn
export MEILI_URL="${meili_url}"
export MEILI_API_KEY="${meili_api_key}"

cd /app
gunicorn --bind 0.0.0.0:5000 main:app 