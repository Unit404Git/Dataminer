@echo off
setlocal

REM 1) Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed.
    echo Opening Microsoft Store page...
    start ms-windows-store://pdp/?productid=9P7QFQMJRFP7
    exit /b 1
)

REM 2) venv
if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate

REM 3) pip + deps
python -m pip install --upgrade pip
pip install -r requirements.txt

REM 4) run
python main_qt.py

endlocal
