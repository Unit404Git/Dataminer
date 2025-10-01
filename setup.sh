#!/usr/bin/env bash
set -euo pipefail

# 1) Python3
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python3 not found. Attempting to install with Homebrew..."
  if command -v brew >/dev/null 2>&1; then
    brew install python
  else
    echo "Homebrew not installed. Please install Python from https://www.python.org/downloads/ and re-run."
    exit 1
  fi
fi

# 2) venv
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate

# 3) pip + deps
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4) run
python main_qt.py
