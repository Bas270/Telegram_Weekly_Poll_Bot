#!/bin/bash
#
# deploy_bot.sh
# Deploys and starts the Telegram bot application.
#
# Usage: ./deploy_bot.sh <project_path>
# Example: ./deploy_bot.sh /opt/telegram-bot
#
# Assumptions:
# - Python 3.10+ is installed
# - Bot script is named bot_prod.py (or bot.py) in the project root
# - vault.json and schedule_config.json exist in the project directory
# - Script is run with appropriate permissions (may need sudo for systemd)
#

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -ne 1 ]; then
    echo "Usage: $0 <project_path>" >&2
    exit 1
fi

PROJECT_PATH="$1"

# Validate project path
if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "${RED}Error: Project directory does not exist: $PROJECT_PATH${NC}" >&2
    exit 1
fi

PROJECT_PATH=$(realpath "$PROJECT_PATH")
cd "$PROJECT_PATH"

echo -e "${GREEN}Deploying bot from: $PROJECT_PATH${NC}"

# ================== SYSTEM DEPENDENCIES ==================
echo ""
echo "Step 1: Installing system dependencies..."

# Check if running as root (for apt install)
if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

# Install system packages if needed
# Note: Adjust packages based on your bot's requirements
SYSTEM_PACKAGES=(
    "python3"
    "python3-pip"
    "python3-venv"
    "git"
)

for pkg in "${SYSTEM_PACKAGES[@]}"; do
    if ! dpkg -l | grep -q "^ii  $pkg "; then
        echo "  Installing $pkg..."
        $SUDO apt-get update -qq
        $SUDO apt-get install -y "$pkg" || {
            echo -e "${YELLOW}Warning: Failed to install $pkg. Continuing...${NC}"
        }
    else
        echo "  $pkg already installed"
    fi
done

# ================== PYTHON VIRTUAL ENVIRONMENT ==================
echo ""
echo "Step 2: Setting up Python virtual environment..."

VENV_DIR="$PROJECT_PATH/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "  Upgrading pip..."
pip install --upgrade pip --quiet

# ================== PYTHON DEPENDENCIES ==================
echo ""
echo "Step 3: Installing Python dependencies..."

if [ -f "requirements.txt" ]; then
    echo "  Installing from requirements.txt..."
    pip install -r requirements.txt || {
        echo -e "${RED}Error: Failed to install Python dependencies${NC}" >&2
        exit 1
    }
else
    echo -e "${YELLOW}Warning: requirements.txt not found. Installing minimal dependencies...${NC}"
    # Install minimal dependencies if requirements.txt is missing
    pip install "python-telegram-bot[job-queue]==21.6" "tzdata>=2024.1" || {
        echo -e "${RED}Error: Failed to install Python dependencies${NC}" >&2
        exit 1
    }
fi

# ================== CONFIGURATION FILES ==================
echo ""
echo "Step 4: Validating configuration files..."

REQUIRED_FILES=("vault.json" "schedule_config.json")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    else
        echo "  ✓ $file found"
    fi
done

if [ ${#MISSING_FILES[@]} -ne 0 ]; then
    echo -e "${RED}Error: Missing required configuration files:${NC}" >&2
    printf '  - %s\n' "${MISSING_FILES[@]}" >&2
    exit 1
fi

# ================== FIND BOT SCRIPT ==================
echo ""
echo "Step 5: Locating bot script..."

BOT_SCRIPT=""
for script in bot_prod.py bot.py bot.py; do
    if [ -f "$script" ]; then
        BOT_SCRIPT="$script"
        echo "  Found: $BOT_SCRIPT"
        break
    fi
done

if [ -z "$BOT_SCRIPT" ]; then
    echo -e "${RED}Error: Bot script not found. Expected: bot_prod.py, bot.py, or bot.py${NC}" >&2
    exit 1
fi

# ================== ENVIRONMENT VARIABLES ==================
echo ""
echo "Step 6: Checking environment variables..."

# Note: vault.json should contain secrets, but if you need additional env vars:
# export TELEGRAM_BOT_TOKEN="..."  # Usually loaded from vault.json
# export TELEGRAM_TARGET_CHAT_ID="..."  # Usually loaded from vault.json

# Check if vault.json is readable
if [ ! -r "vault.json" ]; then
    echo -e "${YELLOW}Warning: vault.json is not readable. Check permissions.${NC}"
fi

# ================== STOP EXISTING BOT (if running) ==================
echo ""
echo "Step 7: Stopping existing bot instance (if any)..."

# Try systemd service first
SERVICE_NAME="telegram-bot-poll"
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo "  Stopping systemd service: $SERVICE_NAME"
    $SUDO systemctl stop "$SERVICE_NAME" || true
fi

# Try screen session
if screen -list | grep -q "telegram-bot"; then
    echo "  Stopping screen session: telegram-bot"
    screen -S telegram-bot -X quit || true
fi

# Try tmux session
if tmux has-session -t telegram-bot 2>/dev/null; then
    echo "  Stopping tmux session: telegram-bot"
    tmux kill-session -t telegram-bot || true
fi

# Kill any remaining Python processes running the bot script
pkill -f "$BOT_SCRIPT" || true
sleep 2

# ================== START BOT ==================
echo ""
echo "Step 8: Starting bot..."

# Choose deployment method
DEPLOY_METHOD="${DEPLOY_METHOD:-systemd}"  # Options: systemd, screen, tmux, direct

case "$DEPLOY_METHOD" in
    systemd)
        echo "  Using systemd service..."
        
        # Create systemd service file
        SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
        WORK_DIR="$PROJECT_PATH"
        PYTHON_BIN="$VENV_DIR/bin/python"
        
        $SUDO tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Telegram Bot Poll Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORK_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PYTHON_BIN $WORK_DIR/$BOT_SCRIPT
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
        
        $SUDO systemctl daemon-reload
        $SUDO systemctl enable "$SERVICE_NAME"
        $SUDO systemctl start "$SERVICE_NAME"
        
        echo -e "${GREEN}Bot started via systemd. Check status with: sudo systemctl status $SERVICE_NAME${NC}"
        echo "View logs with: sudo journalctl -u $SERVICE_NAME -f"
        ;;
    
    screen)
        echo "  Using screen session..."
        screen -dmS telegram-bot bash -c "cd $PROJECT_PATH && source $VENV_DIR/bin/activate && python $BOT_SCRIPT"
        sleep 1
        if screen -list | grep -q "telegram-bot"; then
            echo -e "${GREEN}Bot started in screen session. Attach with: screen -r telegram-bot${NC}"
        else
            echo -e "${RED}Error: Failed to start bot in screen${NC}" >&2
            exit 1
        fi
        ;;
    
    tmux)
        echo "  Using tmux session..."
        tmux new-session -d -s telegram-bot "cd $PROJECT_PATH && source $VENV_DIR/bin/activate && python $BOT_SCRIPT"
        sleep 1
        if tmux has-session -t telegram-bot 2>/dev/null; then
            echo -e "${GREEN}Bot started in tmux session. Attach with: tmux attach -t telegram-bot${NC}"
        else
            echo -e "${RED}Error: Failed to start bot in tmux${NC}" >&2
            exit 1
        fi
        ;;
    
    direct)
        echo "  Starting bot directly (foreground)..."
        echo -e "${YELLOW}Note: Bot will run in foreground. Press Ctrl+C to stop.${NC}"
        python "$BOT_SCRIPT"
        ;;
    
    *)
        echo -e "${RED}Error: Unknown deployment method: $DEPLOY_METHOD${NC}" >&2
        echo "Set DEPLOY_METHOD to: systemd, screen, tmux, or direct"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Deployment completed successfully!${NC}"