#!/bin/bash
# URL To Video Downloader Bot - VPS Deploy Script
# Usage: bash deploy.sh

set -e

echo "================================"
echo " URL To Video Downloader Bot"
echo " VPS Deploy Script"
echo "================================"
echo ""

INSTALL_DIR="/opt/urltovideo"
REPO_URL="https://github.com/itachiplub-cloud/urltovideo.git"

# Check root
if [ "$EUID" -ne 0 ]; then
    echo "[ERROR] Run as root: sudo bash deploy.sh"
    exit 1
fi

# Install system dependencies
echo "[1/6] Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv ffmpeg git > /dev/null 2>&1
echo "[OK] System dependencies installed"

# Clone or update repo
echo "[2/6] Setting up project..."
if [ -d "$INSTALL_DIR" ]; then
    cd "$INSTALL_DIR"
    git pull origin main 2>/dev/null || true
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi
echo "[OK] Project ready"

# Create virtual environment
echo "[3/6] Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "[OK] Python environment ready"

# Create .env if not exists
echo "[4/6] Checking configuration..."
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found. Creating template..."
    cat > .env << 'EOF'
API_ID=
API_HASH=
BOT_TOKEN=
MONGO_URI=
OWNER_ID=
YUKI_API_URL=
YUKI_UPLOAD_ENDPOINT=/upload
EOF
    echo "[ACTION REQUIRED] Edit /opt/urltovideo/.env with your values"
    echo "  nano /opt/urltovideo/.env"
fi

# Create directories
mkdir -p downloads cache logs

# Install systemd service
echo "[5/6] Installing systemd service..."
cp urltovideo.service /etc/systemd/system/
systemctl daemon-reload
echo "[OK] Systemd service installed"

# Start service
echo "[6/6] Starting bot..."
systemctl enable urltovideo > /dev/null 2>&1
systemctl restart urltovideo
echo "[OK] Bot started"

echo ""
echo "================================"
echo " Deploy Complete!"
echo "================================"
echo ""
echo "Service commands:"
echo "  status:  systemctl status urltovideo"
echo "  restart: systemctl restart urltovideo"
echo "  stop:    systemctl stop urltovideo"
echo "  logs:    journalctl -u urltovideo -f"
echo "  edit:    nano /opt/urltovideo/.env"
echo ""
