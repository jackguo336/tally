#! /bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "../venv" ]; then
    python3 -m venv ../venv
fi

# Use virtual environment
source ../venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install command line tool
pipx install . --force
