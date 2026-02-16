# Auto-Start Guide: Telegram Bot on Linux Server Reboot

This guide provides step-by-step instructions to make your Telegram bot automatically start on server reboot using systemd (recommended method for Ubuntu/Linux).

---

## Prerequisites

✅ Bot is already installed and working  
✅ Virtual environment is set up  
✅ Configuration files (`vault.json`, `bot_config.json`) are configured  
✅ Bot runs successfully with `python3 bot.py`

---

## Method 1: Systemd Service (Recommended)

Systemd is the standard service manager on Ubuntu 24.04 LTS. This method provides:
- ✅ Automatic startup on boot
- ✅ Automatic restart on failure
- ✅ Logging via journald
- ✅ Easy management with `systemctl`

### Step 1: Create Systemd Service File

Create the service file:

```bash
sudo nano /etc/systemd/system/telegram-bot-poll.service
```

Copy and paste this content (adjust paths if needed):

```ini
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
```

**Important:** Adjust these paths if your setup is different:
- `User=root` - Change if running as different user
- `WorkingDirectory=/root/Telegram_Weekly_Poll_Bot` - Your bot directory
- `ExecStart=/root/Telegram_Weekly_Poll_Bot/venv/bin/python3` - Path to Python in venv
- `/root/Telegram_Weekly_Poll_Bot/bot.py` - Your bot script path

### Step 2: Reload Systemd

After creating the service file, reload systemd to recognize it:

```bash
sudo systemctl daemon-reload
```

### Step 3: Enable the Service (Auto-Start on Boot)

Enable the service to start automatically on boot:

```bash
sudo systemctl enable telegram-bot-poll.service
```

### Step 4: Start the Service

Start the service immediately (don't wait for reboot):

```bash
sudo systemctl start telegram-bot-poll.service
```

### Step 5: Check Status

Verify the service is running:

```bash
sudo systemctl status telegram-bot-poll.service
```

You should see:
```
● telegram-bot-poll.service - Telegram Weekly Poll Bot Service
     Loaded: loaded (/etc/systemd/system/telegram-bot-poll.service; enabled)
     Active: active (running) since ...
```

### Step 6: View Logs

View real-time logs:

```bash
sudo journalctl -u telegram-bot-poll.service -f
```

View last 50 lines:

```bash
sudo journalctl -u telegram-bot-poll.service -n 50
```

---

## Service Management Commands

### Start/Stop/Restart

```bash
# Start the bot
sudo systemctl start telegram-bot-poll.service

# Stop the bot
sudo systemctl stop telegram-bot-poll.service

# Restart the bot
sudo systemctl restart telegram-bot-poll.service

# Check status
sudo systemctl status telegram-bot-poll.service
```

### Enable/Disable Auto-Start

```bash
# Enable auto-start on boot
sudo systemctl enable telegram-bot-poll.service

# Disable auto-start on boot
sudo systemctl disable telegram-bot-poll.service

# Check if enabled
sudo systemctl is-enabled telegram-bot-poll.service
```

### View Logs

```bash
# Follow logs in real-time
sudo journalctl -u telegram-bot-poll.service -f

# View logs since today
sudo journalctl -u telegram-bot-poll.service --since today

# View logs since specific time
sudo journalctl -u telegram-bot-poll.service --since "2026-02-16 10:00:00"

# View last N lines
sudo journalctl -u telegram-bot-poll.service -n 100
```

---

## Testing Auto-Start

### Test 1: Reboot Server

```bash
sudo reboot
```

After reboot, check if bot started:

```bash
sudo systemctl status telegram-bot-poll.service
```

### Test 2: Simulate Failure

Kill the bot process and verify it restarts automatically:

```bash
# Find bot process
ps aux | grep bot.py

# Kill it (replace PID with actual process ID)
sudo kill <PID>

# Wait 10 seconds, then check status
sudo systemctl status telegram-bot-poll.service
```

The service should automatically restart within 10 seconds (RestartSec=10).

---

## Troubleshooting

### Issue: Service Fails to Start

**Check logs:**
```bash
sudo journalctl -u telegram-bot-poll.service -n 50
```

**Common causes:**
1. **Wrong paths** - Verify all paths in service file are correct
2. **Python not found** - Check venv Python path exists
3. **Missing dependencies** - Ensure requirements.txt is installed
4. **Permission issues** - Check file permissions

**Fix paths:**
```bash
# Find your Python path
which python3
# or
ls -la /root/Telegram_Weekly_Poll_Bot/venv/bin/python3

# Verify bot.py exists
ls -la /root/Telegram_Weekly_Poll_Bot/bot.py
```

### Issue: Service Starts but Bot Doesn't Work

**Check if it's actually running:**
```bash
ps aux | grep bot.py
```

**Check detailed logs:**
```bash
sudo journalctl -u telegram-bot-poll.service -f
```

**Common issues:**
- Configuration files missing or invalid
- Network issues
- Bot token invalid

### Issue: Service Keeps Restarting

If status shows "restarting" repeatedly:

```bash
# Check logs for errors
sudo journalctl -u telegram-bot-poll.service -n 100

# Stop service temporarily
sudo systemctl stop telegram-bot-poll.service

# Run bot manually to see errors
cd /root/Telegram_Weekly_Poll_Bot
source venv/bin/activate
python3 bot.py
```

### Issue: Permission Denied

If you see permission errors:

```bash
# Check file permissions
ls -la /root/Telegram_Weekly_Poll_Bot/bot.py
ls -la /root/Telegram_Weekly_Poll_Bot/vault.json
ls -la /root/Telegram_Weekly_Poll_Bot/bot_config.json

# Make sure service user can read files
# If running as root, this shouldn't be an issue
```

---

## Alternative Methods

### Method 2: Using Screen (Simple but Less Robust)

Create a startup script:

```bash
nano /root/start_bot.sh
```

Add:
```bash
#!/bin/bash
cd /root/Telegram_Weekly_Poll_Bot
source venv/bin/activate
python3 bot.py
```

Make executable:
```bash
chmod +x /root/start_bot.sh
```

Add to crontab:
```bash
crontab -e
```

Add line:
```
@reboot /root/start_bot.sh
```

**Note:** This method doesn't provide automatic restart on failure.

### Method 3: Using Supervisor (Advanced)

Install supervisor:
```bash
sudo apt install supervisor -y
```

Create config:
```bash
sudo nano /etc/supervisor/conf.d/telegram-bot.conf
```

Add:
```ini
[program:telegram-bot-poll]
command=/root/Telegram_Weekly_Poll_Bot/venv/bin/python3 /root/Telegram_Weekly_Poll_Bot/bot.py
directory=/root/Telegram_Weekly_Poll_Bot
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/telegram-bot.err.log
stdout_logfile=/var/log/telegram-bot.out.log
```

Reload and start:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start telegram-bot-poll
```

---

## Complete Setup Script

Here's a complete script to set up auto-start:

```bash
#!/bin/bash
# Save as: setup_autostart.sh

BOT_DIR="/root/Telegram_Weekly_Poll_Bot"
SERVICE_NAME="telegram-bot-poll"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Create service file
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Telegram Weekly Poll Bot Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${BOT_DIR}
Environment="PATH=${BOT_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${BOT_DIR}/venv/bin/python3 ${BOT_DIR}/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable "${SERVICE_NAME}.service"
sudo systemctl start "${SERVICE_NAME}.service"

# Show status
echo "Service status:"
sudo systemctl status "${SERVICE_NAME}.service"

echo ""
echo "Setup complete! Bot will start automatically on reboot."
echo "View logs with: sudo journalctl -u ${SERVICE_NAME}.service -f"
```

Make executable and run:
```bash
chmod +x setup_autostart.sh
sudo ./setup_autostart.sh
```

---

## Quick Reference

### One-Line Setup

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

### Verify Everything Works

```bash
# Check service status
sudo systemctl status telegram-bot-poll.service

# Check if enabled for boot
sudo systemctl is-enabled telegram-bot-poll.service

# View logs
sudo journalctl -u telegram-bot-poll.service -f

# Test reboot (optional)
sudo reboot
```

---

## Notes

1. **Typo Fix**: You typed `pyhton` instead of `python` - use `python3 bot.py`

2. **User Permissions**: If you want to run as a non-root user:
   - Change `User=root` to `User=yourusername`
   - Ensure that user has read access to bot files
   - Adjust paths accordingly

3. **Environment Variables**: If your bot needs environment variables, add them:
   ```ini
   Environment="VAR1=value1"
   Environment="VAR2=value2"
   ```

4. **Multiple Bots**: If running multiple bots, create separate service files with different names.

---

## Summary

✅ **Best Method**: Systemd service (Method 1)  
✅ **Auto-start**: Enabled with `systemctl enable`  
✅ **Auto-restart**: Configured with `Restart=always`  
✅ **Logging**: Available via `journalctl`  
✅ **Management**: Easy with `systemctl` commands  

Your bot will now automatically start on every server reboot and restart if it crashes!
