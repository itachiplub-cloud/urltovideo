# URL To Video Downloader Bot - Windows Setup Script
# Run as Administrator if needed

Write-Host "================================" -ForegroundColor Cyan
Write-Host " URL To Video Downloader Bot" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
$python = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $python) {
    Write-Host "[ERROR] Python not found. Install Python 3.11+" -ForegroundColor Red
    Write-Host "Download: https://python.org/downloads" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Python found" -ForegroundColor Green

# Check FFmpeg
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) {
    Write-Host "[WARNING] FFmpeg not found in PATH" -ForegroundColor Yellow
    Write-Host "Download: https://ffmpeg.org/download.html" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "[OK] FFmpeg found" -ForegroundColor Green
}

# Check .env
if (-not (Test-Path ".env")) {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    Write-Host "Creating template .env file..." -ForegroundColor Yellow

    $envContent = @"
API_ID=
API_HASH=
BOT_TOKEN=
MONGO_URI=
OWNER_ID=
YUKI_API_URL=
YUKI_UPLOAD_ENDPOINT=/upload
"@
    Set-Content -Path ".env" -Value $envContent
    Write-Host "Please edit .env with your values." -ForegroundColor Yellow
    Start-Process notepad ".env"
    exit 1
}

Write-Host "[OK] .env file found" -ForegroundColor Green

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt -q

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Dependencies installed" -ForegroundColor Green
Write-Host ""

# Start bot
Write-Host "Starting bot..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""
python main.py
