@echo off
TITLE Trading Intelligence Backend Server
echo ==========================================================
echo       Trading Intelligence Backend Startup Script
echo ==========================================================
echo.

REM 1. Check if backend/.env exists, if not copy from .env.example
if not exist "backend\.env" (
    echo [INFO] backend\.env not found.
    if exist ".env.example" (
        echo [INFO] Creating backend\.env from .env.example...
        copy ".env.example" "backend\.env" > nul
        echo [SUCCESS] Created backend\.env. Please configure it if needed.
    ) else (
        echo [WARNING] .env.example not found. Please create backend\.env manually.
    )
)

REM 2. Check if virtual environment exists
if not exist "backend\.venv" (
    echo [ERROR] Virtual environment (.venv) not found in backend folder!
    echo Please ensure python virtual environment is set up.
    echo.
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment and starting server...
echo.

REM 3. Run the backend server
cd backend
call .venv\Scripts\activate.bat
python run.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Server crashed or failed to start.
    pause
)
