@echo off
setlocal

echo ========================================================
echo  eFootball Auto Advance - Windows Setup Helper
echo ========================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10 or newer and make sure "Add python.exe to PATH" is checked.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Checking / Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo  - Created new virtual environment in 'venv\'.
) else (
    echo  - Existing 'venv\' found.
)

echo.
echo [2/3] Installing cross-platform requirements...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo [3/3] Testing input system...
python test_controller.py

echo.
echo ========================================================
echo  Setup Complete!
echo ========================================================
echo.
echo To run the bot on Windows:
echo   1. Make sure eFootball is running in Borderless Windowed mode.
echo   2. Run: venv\Scripts\python.exe bot.py --input keyboard
echo      (Or 'bot.py --input controller' if you installed ViGEmBus)
echo.
pause
