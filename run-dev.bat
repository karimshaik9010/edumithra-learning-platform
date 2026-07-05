@echo off
title EDUMITHRA Launcher
echo =====================================================================
echo               EDUMITHRA -- AI Learning Copilot Dev Launcher
echo =====================================================================
echo.
echo This script starts both the FastAPI Backend and the Next.js Frontend.
echo Make sure Python and Node.js are installed and in your system PATH.
echo.

set PROJECT_DIR=%~dp0
set BACKEND_DIR=%PROJECT_DIR%backend
set FRONTEND_DIR=%PROJECT_DIR%frontend

echo ---------------------------------------------------------------------
echo [1/3] Preparing Python Backend...
echo ---------------------------------------------------------------------
cd /d "%BACKEND_DIR%"
if not exist venv (
    echo Creating python virtual environment in venv/...
    python -m venv venv
)
echo Activating virtual environment & installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.

echo ---------------------------------------------------------------------
echo [2/3] Preparing Next.js Frontend...
echo ---------------------------------------------------------------------
cd /d "%FRONTEND_DIR%"
echo Installing package dependencies via npm...
call npm install
echo.

echo ---------------------------------------------------------------------
echo [3/3] Spawning Dev Servers...
echo ---------------------------------------------------------------------
echo Launching FastAPI backend server at http://127.0.0.1:8000 ...
cd /d "%BACKEND_DIR%"
start "EDUMITHRA Backend (FastAPI)" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo Launching Next.js frontend dev server at http://localhost:3000 ...
cd /d "%FRONTEND_DIR%"
start "EDUMITHRA Frontend (Next.js)" cmd /k "npm run dev"

echo.
echo =====================================================================
echo Boot processes triggered! 
echo Backend will be running at: http://127.0.0.1:8000
echo Frontend will be running at: http://localhost:3000
echo.
echo Check the spawned windows for logs. Enjoy learning!
echo =====================================================================
pause
