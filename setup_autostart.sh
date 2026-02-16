#!/bin/bash
#
# Auto-Start Setup Script for Telegram Weekly Poll Bot
# This script creates a systemd service for automatic startup on reboot
#

set -e  # Exit on error

BOT_DIR="/root/Telegram_Weekly_Poll_Bot"
SERVICE_NAME="telegram-bot-poll"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
PYTHON_PATH="${BOT_DIR}/venv/bin/python3"
BOT_SCRIPT="${BOT_DIR}/bot.py"

echo "=========================================="
echo "Telegram Bot Auto-Start Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Error: This script must be run as root (use sudo)"
    exit 1
fi

# Verify bot directory exists
if [ ! -d "$BOT_DIR" ]; then
    echo "Error: Bot directory not found: $BOT_DIR"
    echo "Please update BOT_DIR in this script or create the directory."
    exit 1
fi

# Verify Python exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "Error: Python not found at: $PYTHON_PATH"
    echo "Make sure virtual environment is set up correctly."
    exit 1
fi

# Verify bot script exists
if [ ! -f "$BOT_SCRIPT" ]; then
    echo "Error: Bot script not found: $BOT_SCRIPT"
    exit 1
fi

echo "Configuration:"
echo "  Bot Directory: $BOT_DIR"
echo "  Python Path: $PYTHON_PATH"
echo "  Bot Script: $BOT_SCRIPT"
echo "  Service Name: $SERVICE_NAME"
echo ""

# Check if service already exists
if [ -f "$SERVICE_FILE" ]; then
    echo "Warning: Service file already exists: $SERVICE_FILE"
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Create service file
echo "Creating systemd service file..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Telegram Weekly Poll Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${BOT_DIR}
Environment="PATH=${BOT_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${PYTHON_PATH} ${BOT_SCRIPT}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service file created: $SERVICE_FILE"
echo ""

# Reload systemd
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "✓ Systemd reloaded"
echo ""

# Stop existing service if running
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo "Stopping existing service..."
    sudo systemctl stop "$SERVICE_NAME"
    echo "✓ Service stopped"
    echo ""
fi

# Enable service (auto-start on boot)
echo "Enabling service for auto-start on boot..."
sudo systemctl enable "$SERVICE_NAME.service"
echo "✓ Service enabled"
echo ""

# Start service
echo "Starting service..."
sudo systemctl start "$SERVICE_NAME.service"
echo "✓ Service started"
echo ""

# Wait a moment for service to start
sleep 2

# Check status
echo "=========================================="
echo "Service Status:"
echo "=========================================="
sudo systemctl status "$SERVICE_NAME.service" --no-pager -l || true
echo ""

# Show useful commands
echo "=========================================="
echo "Useful Commands:"
echo "=========================================="
echo "  Check status:  sudo systemctl status $SERVICE_NAME.service"
echo "  View logs:     sudo journalctl -u $SERVICE_NAME.service -f"
echo "  Stop bot:       sudo systemctl stop $SERVICE_NAME.service"
echo "  Start bot:      sudo systemctl start $SERVICE_NAME.service"
echo "  Restart bot:    sudo systemctl restart $SERVICE_NAME.service"
echo "  Disable auto-start: sudo systemctl disable $SERVICE_NAME.service"
echo ""

# Verify it's enabled
if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo "✓ Service is enabled for auto-start on boot"
else
    echo "⚠ Warning: Service may not be enabled properly"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Your bot will now:"
echo "  ✓ Start automatically on server reboot"
echo "  ✓ Restart automatically if it crashes"
echo "  ✓ Log output to systemd journal"
echo ""
echo "Test by rebooting: sudo reboot"
echo ""
