#! /bin/bash

# Create virtual environment
python3 -m venv ../venv

# Use virtual environment
source ../venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install command line tool
pipx install . --force
