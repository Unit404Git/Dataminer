#!/usr/bin/env bash
set -euo pipefail

# 1) Python3
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python3 not found. Attempting to install with Homebrew..."
  if command -v brew >/dev/null 2>&1; then
    brew install python
  else
    echo "Please install Python from https://www.python.org/downloads/ and re-run."
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

# 4) compile Qt resources -> resources_rc.py
if ! command -v pyside6-rcc >/dev/null 2>&1; then
  echo "pyside6-rcc not found (should come with PySide6)."
  echo "Trying to run via module..."
  python - <<'PY'
import sys, subprocess
subprocess.check_call([sys.executable, "-m", "PySide6.scripts.pyside_tool", "rcc", "resources.qrc", "-o", "resources_rc.py"])
PY
else
  pyside6-rcc resources.qrc -o resources_rc.py
fi

# 5) run
python main_qt.py
