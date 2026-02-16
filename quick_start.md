# Quick Start Guide

## First Time Setup

```bash
# 1. Clone repository
./pull_project.sh git@github.com:username/repo.git /home/username/bot_project

# 2. Deploy bot with auto-start
cd /home/username/bot_project
./launch_bot.sh --setup-autostart
```

## Update Code & Restart

```bash
# 1. Pull latest code
./pull_project.sh git@github.com:username/repo.git /home/username/bot_project

# 2. Restart bot
cd /home/username/bot_project
./launch_bot.sh --setup-autostart
```

## Check Bot Status

```bash
sudo systemctl status telegram-bot-poll
```

## View Logs

```bash
sudo journalctl -u telegram-bot-poll -f
```

## Stop Bot

```bash
sudo systemctl stop telegram-bot-poll
```

## Start Bot

```bash
sudo systemctl start telegram-bot-poll
```

---

**See `SCRIPT_INTEGRATION_GUIDE.md` for detailed documentation.**