#!/bin/bash

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python requirements
python3 -m pip install -r requirements.txt

# Run Python script
python3 app/client.py

# Deactivate virtual environment
deactivate
