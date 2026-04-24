@echo off
setlocal
cd /d %~dp0

echo [Anima LoRA Factory] Initializing...

:: Create virtual environment if it doesn't exist
if not exist venv\ (
    echo [INFO] Creating virtual environment venv...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Run setup check
python backend/setup_check.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Setup check failed. Please check the messages above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [Anima LoRA Factory] Starting backend server...
echo Access the GUI at http://localhost:8000
echo.

:: Start browser
start http://localhost:8000

:: Run backend
cd backend
python main.py

pause
