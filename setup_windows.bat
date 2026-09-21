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

echo [1/4] Checking / Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo  - Created new virtual environment in 'venv\'.
) else (
    echo  - Existing 'venv\' found.
)

echo.
echo [2/4] Installing cross-platform requirements...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo [3/4] Checking ViGEmBus Controller Driver...
sc query ViGEmBus >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo  - ViGEmBus driver is already installed.
) else (
    echo  - [NOTICE] ViGEmBus controller driver is not detected on your system.
    echo    This driver enables virtual Xbox 360 controller emulation on Windows.
    echo.
    set /p INSTALL_VIGEM="    Would you like to download and install ViGEmBus from official GitHub? [Y/N]: "
    if /i "%INSTALL_VIGEM%"=="Y" (
        echo    Downloading ViGEmBus_Setup_1.22.0.exe from official GitHub...
        curl -L -f -o ViGEmBus_Setup.exe https://github.com/nefarius/ViGEmBus/releases/download/v1.22.0/ViGEmBus_Setup_1.22.0.exe 2>nul || powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://github.com/nefarius/ViGEmBus/releases/download/v1.22.0/ViGEmBus_Setup_1.22.0.exe', 'ViGEmBus_Setup.exe')"
        if exist "ViGEmBus_Setup.exe" (
            echo    Launching installer... (Please click 'Yes' on the Windows administrator prompt)
            start /wait ViGEmBus_Setup.exe
            del ViGEmBus_Setup.exe >nul 2>nul
            echo    Installer finished.
        ) else (
            echo    [WARNING] Download failed. You can install it manually from:
            echo    https://github.com/nefarius/ViGEmBus/releases
        )
    ) else (
        echo    Skipped driver installation. You can run the bot with '--input keyboard'.
    )
)

echo.
echo [4/4] Testing input system...
python test_controller.py

echo.
echo ========================================================
echo  Setup Complete!
echo ========================================================
echo.
echo To run the bot on Windows:
echo   1. Ensure ViGEmBus is installed: https://github.com/nefarius/ViGEmBus/releases
echo   2. Make sure eFootball is running in Borderless Windowed mode.
echo   3. Choose how to run the bot:
echo      - Default (Both Keyboard + Controller):
echo          venv\Scripts\python.exe bot.py
echo      - Keyboard only (Enter):
echo          venv\Scripts\python.exe bot.py --input keyboard
echo      - Controller only (A button):
echo          venv\Scripts\python.exe bot.py --input controller
echo.
pause
