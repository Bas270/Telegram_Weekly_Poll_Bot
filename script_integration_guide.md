# Script Integration Guide

This document explains how `pull_project.sh`, `deploy_bot.sh`, and `launch_bot.sh` work together to manage your Telegram bot deployment on Ubuntu 24.04 LTS.

---

## Script Overview

### 1. `pull_project.sh` - Repository Management
**Purpose:** Clone or update the GitHub repository

**What it does:**
- Clones repository if it doesn't exist
- Pulls latest changes if repository exists
- Handles authentication (SSH/HTTPS)
- Validates git repository state

**When to use:** 
- Initial setup
- When you want to update code from GitHub
- Before deploying new changes

---

### 2. `deploy_bot.sh` - Full Deployment
**Purpose:** Complete deployment with system setup

**What it does:**
- Installs system dependencies (apt packages)
- Creates/updates Python virtual environment
- Installs Python dependencies
- Validates all configuration files
- Stops existing bot instances
- Starts bot with chosen method (systemd/screen/tmux/direct)
- **More comprehensive** - handles system-level setup

**When to use:**
- First-time deployment on a new server
- When system dependencies need updating
- When you want full control over deployment method
- Production deployments

---

### 3. `launch_bot.sh` - Quick Launch & Auto-Start Setup
**Purpose:** Simple launch with optional auto-start configuration

**What it does:**
- Creates/activates Python virtual environment
- Installs dependencies from requirements.txt
- Launches bot directly or configures systemd service
- **Simpler** - focuses on launching and auto-start setup

**When to use:**
- Quick restarts after code updates
- Setting up auto-start on reboot
- Development/testing
- When system dependencies are already installed

---

## Recommended Workflow

### Initial Setup (First Time)

```bash
# Step 1: Clone repository
./pull_project.sh git@github.com:username/repo.git /home/username/bot_project

# Step 2: Full deployment (installs everything)
./deploy_bot.sh /home/username/bot_project

# OR use launch_bot.sh with auto-start
cd /home/username/bot_project
./launch_bot.sh --setup-autostart
```

### Regular Updates (Code Changes)

```bash
# Step 1: Pull latest code
./pull_project.sh git@github.com:username/repo.git /home/username/bot_project

# Step 2: Quick launch (if dependencies haven't changed)
cd /home/username/bot_project
./launch_bot.sh --setup-autostart

# OR full redeploy (if dependencies changed or you want fresh setup)
./deploy_bot.sh /home/username/bot_project
```

### After Server Reboot

If you've configured auto-start with `launch_bot.sh --setup-autostart` or `deploy_bot.sh` (systemd method), the bot will start automatically. Otherwise:

```bash
cd /home/username/bot_project
./launch_bot.sh --setup-autostart
```

---

## Detailed Comparison

| Feature | `pull_project.sh` | `deploy_bot.sh` | `launch_bot.sh` |
|---------|------------------|-----------------|-----------------|
| **Git Operations** | ✅ Clone/Pull | ❌ | ❌ |
| **System Packages** | ❌ | ✅ Installs apt packages | ❌ |
| **Python Venv** | ❌ | ✅ Creates/updates | ✅ Creates/activates |
| **Dependencies** | ❌ | ✅ Installs | ✅ Installs |
| **Config Validation** | ❌ | ✅ Full validation | ✅ Basic check |
| **Deployment Methods** | ❌ | ✅ systemd/screen/tmux/direct | ✅ systemd/direct |
| **Auto-Start Setup** | ❌ | ✅ (systemd) | ✅ (systemd) |
| **Complexity** | Low | High | Medium |
| **Use Case** | Code updates | Full deployment | Quick launch |

---

## Execution Order Examples

### Scenario 1: Fresh Server Setup

```bash
# 1. Pull code from GitHub
./pull_project.sh git@github.com:user/repo.git /home/username/bot_project

# 2. Full deployment (installs everything)
./deploy_bot.sh /home/username/bot_project
# OR
cd /home/username/bot_project && ./launch_bot.sh --setup-autostart
```

### Scenario 2: Code Update Only

```bash
# 1. Pull latest code
./pull_project.sh git@github.com:user/repo.git /home/username/bot_project

# 2. Quick restart (if no dependency changes)
cd /home/username/bot_project
./launch_bot.sh --setup-autostart
```

### Scenario 3: Dependency Update

```bash
# 1. Pull latest code
./pull_project.sh git@github.com:user/repo.git /home/username/bot_project

# 2. Full redeploy (to update dependencies)
./deploy_bot.sh /home/username/bot_project
```

### Scenario 4: Server Reboot Recovery

```bash
# If auto-start is configured, bot starts automatically
# Otherwise, manually launch:
cd /home/username/bot_project
./launch_bot.sh --setup-autostart
```

---

## Role of Each Script

### `pull_project.sh` - Code Management
- **Role:** Keeps code synchronized with GitHub
- **Dependencies:** Git, SSH key or HTTPS credentials
- **Output:** Updated project directory
- **Idempotent:** Safe to run multiple times

### `deploy_bot.sh` - Infrastructure Setup
- **Role:** Sets up complete deployment environment
- **Dependencies:** sudo access (for system packages)
- **Output:** Fully configured and running bot
- **Idempotent:** Safe to run multiple times (stops existing instances)

### `launch_bot.sh` - Application Launch
- **Role:** Quick launch with minimal setup
- **Dependencies:** Python, project directory exists
- **Output:** Running bot (foreground or systemd service)
- **Idempotent:** Stops existing instances before starting

---

## Auto-Start Configuration

Both `deploy_bot.sh` (with systemd method) and `launch_bot.sh --setup-autostart` configure systemd service for auto-start on reboot.

### Systemd Service Details

**Service Name:** `telegram-bot-poll`

**Service File:** `/etc/systemd/system/telegram-bot-poll.service`

**Features:**
- Starts automatically on boot
- Restarts on failure (RestartSec=10)
- Logs to journald
- Runs as current user

**Management:**
```bash
# Check status
sudo systemctl status telegram-bot-poll

# View logs
sudo journalctl -u telegram-bot-poll -f

# Stop bot
sudo systemctl stop telegram-bot-poll

# Start bot
sudo systemctl start telegram-bot-poll

# Restart bot
sudo systemctl restart telegram-bot-poll

# Disable auto-start
sudo systemctl disable telegram-bot-poll

# Enable auto-start
sudo systemctl enable telegram-bot-poll
```

---

## Alternative: Crontab Auto-Start

If you prefer crontab over systemd, you can add this to your crontab:

```bash
# Edit crontab
crontab -e

# Add this line (runs on reboot)
@reboot cd /home/username/bot_project && /home/username/bot_project/venv/bin/python /home/username/bot_project/bot.py >> /home/username/bot_project/bot.log 2>&1
```

**Note:** Systemd is recommended over crontab for better process management, logging, and restart policies.

---

## Best Practices

1. **Always pull code first** before deploying:
   ```bash
   ./pull_project.sh <repo_url> <project_dir>
   ```

2. **Use `deploy_bot.sh` for initial setup** or when dependencies change

3. **Use `launch_bot.sh` for quick restarts** after code-only updates

4. **Configure auto-start** using `--setup-autostart` flag or systemd method in `deploy_bot.sh`

5. **Check logs regularly**:
   ```bash
   sudo journalctl -u telegram-bot-poll -f
   ```

6. **Keep scripts executable**:
   ```bash
   chmod +x pull_project.sh deploy_bot.sh launch_bot.sh
   ```

---

## Troubleshooting

### Bot Not Starting After Reboot

1. Check if systemd service is enabled:
   ```bash
   sudo systemctl is-enabled telegram-bot-poll
   ```

2. Check service status:
   ```bash
   sudo systemctl status telegram-bot-poll
   ```

3. View recent logs:
   ```bash
   sudo journalctl -u telegram-bot-poll -n 50
   ```

### Virtual Environment Issues

If venv is corrupted:
```bash
cd /home/username/bot_project
rm -rf venv
./launch_bot.sh --setup-autostart
```

### Configuration File Issues

Ensure these files exist:
- `vault.json` - Bot token and chat ID
- `schedule_config.json` - Scheduling parameters
- `requirements.txt` - Python dependencies

---

## Summary

- **`pull_project.sh`**: Manages code synchronization with GitHub
- **`deploy_bot.sh`**: Complete deployment solution (system setup + launch)
- **`launch_bot.sh`**: Quick launch solution (app setup + launch)

**Recommended flow:**
1. `pull_project.sh` → Get latest code
2. `deploy_bot.sh` OR `launch_bot.sh --setup-autostart` → Deploy/Launch
3. Bot runs automatically on reboot (if systemd configured)

All scripts are designed to be idempotent and safe to run multiple times.
