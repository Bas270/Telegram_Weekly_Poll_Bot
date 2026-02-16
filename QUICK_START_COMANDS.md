# Quick Start Commands - Auto-Start Setup

## Fastest Setup (Copy & Paste)

```bash
# 1. Download and run setup script
cd /root/Telegram_Weekly_Poll_Bot
wget https://raw.githubusercontent.com/your-repo/setup_autostart.sh
chmod +x setup_autostart.sh
sudo ./setup_autostart.sh
```

## Manual Setup (Step by Step)

```bash
# 1. Create service file
sudo nano /etc/systemd/system/telegram-bot-poll.service

# 2. Copy content from telegram-bot-poll.service file

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Enable auto-start
sudo systemctl enable telegram-bot-poll.service

# 5. Start service
sudo systemctl start telegram-bot-poll.service

# 6. Check status
sudo systemctl status telegram-bot-poll.service
```

## One-Line Setup

```bash
sudo bash -c 'cat > /etc/systemd/system/telegram-bot-poll.service << EOF
[Unit]
Description=Telegram Weekly Poll Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/Telegram_Weekly_Poll_Bot
Environment="PATH=/root/Telegram_Weekly_Poll_Bot/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/root/Telegram_Weekly_Poll_Bot/venv/bin/python3 /root/Telegram_Weekly_Poll_Bot/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload && sudo systemctl enable telegram-bot-poll.service && sudo systemctl start telegram-bot-poll.service'
```

## Essential Commands

```bash
# Check if bot is running
sudo systemctl status telegram-bot-poll.service

# View live logs
sudo journalctl -u telegram-bot-poll.service -f

# Restart bot
sudo systemctl restart telegram-bot-poll.service

# Stop bot
sudo systemctl stop telegram-bot-poll.service

# Check if enabled for boot
sudo systemctl is-enabled telegram-bot-poll.service
```

## Troubleshooting

```bash
# View recent errors
sudo journalctl -u telegram-bot-poll.service -n 50 --no-pager

# Check if service exists
ls -la /etc/systemd/system/telegram-bot-poll.service

# Test bot manually (if service fails)
cd /root/Telegram_Weekly_Poll_Bot
source venv/bin/activate
python3 bot.py
```
