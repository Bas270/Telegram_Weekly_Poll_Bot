#!/bin/bash
#
# launch_bot.sh
# Activates/creates Python virtual environment, installs dependencies,
# launches the bot, and optionally configures auto-start on reboot.
#
# Usage: ./launch_bot.sh [--setup-autostart]
#   --setup-autostart: Configure systemd service for auto-start on reboot
#
# Assumptions:
# - Project directory: /home/username/bot_project
# - Main bot script: bot.py
# - requirements.txt exists in project directory
# - Python 3.10+ is installed
#

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration - adjust these paths as needed
PROJECT_DIR="${PROJECT_DIR:-/home/username/bot_project}"
BOT_SCRIPT="${BOT_SCRIPT:-bot.py}"
VENV_DIR="$PROJECT_DIR/venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if --setup-autostart flag is provided
SETUP_AUTOSTART=false
if [[ "${1:-}" == "--setup-autostart" ]]; then
    SETUP_AUTOSTART=true
fi

echo -e "${GREEN}=== Bot Launch Script ===${NC}"
echo "Project directory: $PROJECT_DIR"
echo "Bot script: $BOT_SCRIPT"
echo ""

# Validate project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}Error: Project directory does not exist: $PROJECT_DIR${NC}" >&2
    exit 1
fi

cd "$PROJECT_DIR"

# ================== STEP 1: CREATE/ACTIVATE VIRTUAL ENVIRONMENT ==================
echo -e "${GREEN}Step 1: Setting up Python virtual environment...${NC}"

if [ ! -d "$VENV_DIR" ]; then
    echo "  Creating new virtual environment at $VENV_DIR"
    python3 -m venv "$VENV_DIR" || {
        echo -e "${RED}Error: Failed to create virtual environment${NC}" >&2
        exit 1
    }
else
    echo "  Virtual environment already exists at $VENV_DIR"
fi

# Activate virtual environment
echo "  Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Verify activation
if [ -z "${VIRTUAL_ENV:-}" ]; then
    echo -e "${RED}Error: Failed to activate virtual environment${NC}" >&2
    exit 1
fi

echo "  ✓ Virtual environment activated: $VIRTUAL_ENV"

# Upgrade pip
echo "  Upgrading pip..."
pip install --upgrade pip --quiet

# ================== STEP 2: INSTALL DEPENDENCIES ==================
echo ""
echo -e "${GREEN}Step 2: Installing dependencies...${NC}"

if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${YELLOW}Warning: requirements.txt not found at $REQUIREMENTS_FILE${NC}"
    echo "  Skipping dependency installation."
else
    echo "  Installing from $REQUIREMENTS_FILE"
    pip install -r "$REQUIREMENTS_FILE" || {
        echo -e "${RED}Error: Failed to install dependencies${NC}" >&2
        exit 1
    }
    echo "  ✓ Dependencies installed successfully"
fi

# ================== STEP 3: VALIDATE BOT SCRIPT ==================
echo ""
echo -e "${GREEN}Step 3: Validating bot script...${NC}"

BOT_SCRIPT_PATH="$PROJECT_DIR/$BOT_SCRIPT"

if [ ! -f "$BOT_SCRIPT_PATH" ]; then
    echo -e "${RED}Error: Bot script not found: $BOT_SCRIPT_PATH${NC}" >&2
    exit 1
fi

if [ ! -x "$BOT_SCRIPT_PATH" ]; then
    echo "  Making bot script executable..."
    chmod +x "$BOT_SCRIPT_PATH"
fi

echo "  ✓ Bot script found: $BOT_SCRIPT_PATH"

# ================== STEP 4: CHECK CONFIGURATION FILES ==================
echo ""
echo -e "${GREEN}Step 4: Checking configuration files...${NC}"

REQUIRED_CONFIG_FILES=("vault.json" "schedule_config.json")
MISSING_FILES=()

for file in "${REQUIRED_CONFIG_FILES[@]}"; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        echo "  ✓ $file found"
    else
        echo -e "${YELLOW}  ⚠ $file not found${NC}"
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -ne 0 ]; then
    echo -e "${YELLOW}Warning: Some configuration files are missing:${NC}"
    printf '  - %s\n' "${MISSING_FILES[@]}"
    echo "  Bot may fail to start without these files."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ================== STEP 5: STOP EXISTING BOT INSTANCE ==================
echo ""
echo -e "${GREEN}Step 5: Stopping existing bot instance (if any)...${NC}"

# Try to stop systemd service
SERVICE_NAME="telegram-bot-poll"
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo "  Stopping systemd service: $SERVICE_NAME"
    sudo systemctl stop "$SERVICE_NAME" || true
fi

# Kill any running Python processes for this bot script
if pgrep -f "$BOT_SCRIPT" > /dev/null; then
    echo "  Stopping running bot processes..."
    pkill -f "$BOT_SCRIPT" || true
    sleep 2
fi

# ================== STEP 6: LAUNCH BOT ==================
echo ""
echo -e "${GREEN}Step 6: Launching bot...${NC}"

# Check if we're setting up autostart or running directly
if [ "$SETUP_AUTOSTART" = true ]; then
    echo "  Configuring systemd service for auto-start..."
    
    # Get current user (for systemd service)
    CURRENT_USER="${SUDO_USER:-$USER}"
    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
    PYTHON_BIN="$VENV_DIR/bin/python"
    
    # Create systemd service file
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Telegram Bot Poll Service
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PYTHON_BIN $PROJECT_DIR/$BOT_SCRIPT
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable/start service
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl start "$SERVICE_NAME"
    
    echo -e "${GREEN}  ✓ Bot configured to start automatically on reboot${NC}"
    echo ""
    echo "Service management commands:"
    echo "  Check status:  sudo systemctl status $SERVICE_NAME"
    echo "  View logs:     sudo journalctl -u $SERVICE_NAME -f"
    echo "  Stop bot:      sudo systemctl stop $SERVICE_NAME"
    echo "  Restart bot:   sudo systemctl restart $SERVICE_NAME"
    echo "  Disable auto-start: sudo systemctl disable $SERVICE_NAME"
    
    # Show current status
    sleep 2
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo ""
        echo -e "${GREEN}✓ Bot is running via systemd service${NC}"
    else
        echo ""
        echo -e "${YELLOW}⚠ Service may have failed to start. Check logs:${NC}"
        echo "  sudo journalctl -u $SERVICE_NAME -n 50"
    fi
    
else
    # Run bot directly in foreground
    echo "  Starting bot in foreground..."
    echo -e "${YELLOW}  Press Ctrl+C to stop${NC}"
    echo ""
    
    # Launch bot
    python "$BOT_SCRIPT_PATH"
fi

echo ""
echo -e "${GREEN}=== Script completed ===${NC}"