@echo off
setlocal

cd /d %~dp0

echo ==========================================
echo   Pose Annotator - Local Startup (Win)
echo   Requires: Python 3.12+
echo ==========================================

REM --- Require Python Launcher + Python 3.12+ ---
py -3.12 --version >nul 2>&1
if errorlevel 1 (
  echo.
  echo ERROR: Python 3.12+ not found via the Python Launcher (py.exe).
  echo Please install Python 3.12+ from https://www.python.org/downloads/windows/
  echo Make sure to check: "Install launcher for all users" (py.exe).
  echo.
  pause
  exit /b 1
)

echo Found:
py -3.12 --version
echo.

REM --- Create venv if missing ---
if not exist .venv (
  echo Creating virtual environment (.venv) with Python 3.12...
  py -3.12 -m venv .venv
)

REM --- Activate venv ---
call .venv\Scripts\activate

REM --- Upgrade pip ---
python -m pip install --upgrade pip

REM --- Install deps ---
pip install -r backend\requirements.txt

REM --- Check frontend build exists ---
if not exist frontend\dist\index.html (
  echo.
  echo ERROR: frontend\dist\index.html not found.
  echo This branch expects the frontend to already be built and included.
  echo.
  pause
  exit /b 1
)

echo.
echo Starting backend at: http://localhost:8000
echo The browser will open automatically.
echo Close this window to stop the server.
echo.

REM --- Open browser (non-blocking) ---
start "" http://localhost:8000

REM --- Start backend ---
python backend\api.py

pause
endlocal