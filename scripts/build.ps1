# Call from the parent directory with `.\scripts\build.ps1`

# Create virtual environment if it doesn't exist
if (!(Test-Path ".\venv")) {
    python -m venv .\venv
}

# Use virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create an executable
pyinstaller tally.spec
