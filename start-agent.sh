#!/bin/bash
cd /home/vps/pulsebnb-croo
set -a
source .env
set +a
exec venv/bin/python3 croo_provider.py
