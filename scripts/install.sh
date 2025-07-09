#! /bin/bash

# Use virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install command line tool
pipx install . --force
