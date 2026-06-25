#!/bin/bash
set -e

cd /var/www/trackers

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Downloading blocklists..."
python3 blocklist.py --update

echo "Installing systemd service..."
sudo cp tracker-expose.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tracker-expose
sudo systemctl start tracker-expose

echo "Done! Check status with: sudo systemctl status tracker-expose"
