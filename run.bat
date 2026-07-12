@echo off
title URL To Video Downloader Bot
echo ================================
echo  URL To Video Downloader Bot
echo ================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg not found in PATH.
    echo Download from https://ffmpeg.org and add to PATH.
    echo.
)

if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Create a .env file with your configuration.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt -q

echo.
echo Starting bot...
python main.py
pause
