#!/usr/bin/env bash
set -e

# Check for Python3
if ! command -v python3 &>/dev/null; then
    echo "Python3 not found. Attempting to install with Homebrew..."
    if command -v brew &>/dev/null; then
        brew install python
    else
        echo "Homebrew not installed. Please install Python manually: https://www.python.org/downloads/"
        exit 1
    fi
fi

# Create venv if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Upgrade pip
pip3 install --upgrade pip

# Install requirements
pip3 install -r requirements.txt

# Run app
python3 main.py
