@echo off
echo ==========================================
echo   WEEX AI Bot - Windows Auto Setup
echo ==========================================
echo.

echo [1/3] Checking for Python...
python --version
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python 3.10+ from python.org
    pause
    exit /b
)

echo.
echo [2/3] Creating Virtual Environment (.venv)...
if not exist ".venv" (
    python -m venv .venv
    echo    - .venv created successfully.
) else (
    echo    - .venv already exists. Skipping creation.
)

echo.
echo [3/3] Installing Dependencies from requirements.txt...
echo    - Activating .venv...
call .venv\Scripts\activate.bat
echo    - Installing packages (this may take a few minutes)...
pip install -r requirements.txt

echo.
echo ==========================================
echo   SETUP COMPLETE!
echo ==========================================
echo.
echo To start the bot, run: 
echo    .venv\Scripts\activate
echo    python src/main.py
echo.
pause
