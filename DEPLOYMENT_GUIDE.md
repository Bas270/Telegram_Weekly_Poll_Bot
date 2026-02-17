### Telegram Weekly Poll Bot – Deployment Guide

This guide explains how to download, configure, run, and safely remove the Telegram Weekly Poll Bot on common operating systems.

The commands below are examples – **adjust paths, usernames, and repository URLs to match your environment**.

---

### 1. Project Download

#### 1.1. Choose an install directory

Decide where the bot will live, for example:

- **Linux**: `/opt/Telegram_Weekly_Poll_Bot` or `/srv/Telegram_Weekly_Poll_Bot`
- **Windows**: `C:\Telegram_Weekly_Poll_Bot`

Create and enter the directory’s parent:

```bash
# Linux example
sudo mkdir -p /opt
cd /opt
```

```powershell
# Windows PowerShell example
New-Item -ItemType Directory -Force -Path "C:\"
Set-Location "C:\"
```

#### 1.2. Clone the repository with git

Replace `<YOUR_GITHUB_USERNAME>` with the actual owner (or use the real HTTPS URL of your repo).

```bash
# Linux / macOS (Bash)
git clone https://github.com/<YOUR_GITHUB_USERNAME>/Telegram_Weekly_Poll_Bot.git
cd Telegram_Weekly_Poll_Bot
```

```powershell
# Windows PowerShell
git clone https://github.com/<YOUR_GITHUB_USERNAME>/Telegram_Weekly_Poll_Bot.git
Set-Location .\Telegram_Weekly_Poll_Bot
```

If `git` is not installed:

- **Debian/Ubuntu**:

```bash
sudo apt update
sudo apt install -y git
```

- **Windows**: install Git for Windows from `https://git-scm.com/` and restart your terminal.

---

### 2. Configuration

The bot uses two main configuration files in the project root:

- `vault.json` – **secrets** (Telegram bot token, chat ID, optional thread ID)
- `bot_config.json` – **survey content and schedule**

#### 2.1. Configure `vault.json`

Create or edit `vault.json` in the project directory.

Example template:

```json
{
  "TELEGRAM_BOT_TOKEN": "YOUR_TELEGRAM_BOT_TOKEN_HERE",
  "TELEGRAM_TARGET_CHAT_ID": "-1001234567890",
  "TELEGRAM_THREAD_ID": 12345
}
```

- **`TELEGRAM_BOT_TOKEN`**: get this from BotFather on Telegram.
- **`TELEGRAM_TARGET_CHAT_ID`**:
  - For private chats: the numeric chat ID.
  - For groups/supergroups: usually starts with `-100`.
- **`TELEGRAM_THREAD_ID`** (optional):
  - Use this if you want polls posted into a specific forum topic/thread.
  - If omitted or `null`, polls go to the main chat.

> **Security note**: `vault.json` contains secrets. Do **not** commit this file to Git or share it publicly.

#### 2.2. Configure `bot_config.json`

Example configuration:

```json
{
  "survey": {
    "title": "How was your week?",
    "options": [
      "Great",
      "Good",
      "Okay",
      "Bad"
    ]
  },
  "schedule": {
    "start_day": "Tuesday",
    "start_time": "12:00",
    "stop_day": "Thursday",
    "stop_time": "20:00",
    "timezone": "Europe/Berlin"
  },
  "thread_id": 12345
}
```

- **`survey.title`**: the poll question.
- **`survey.options`**:
  - 2–10 non-empty option strings.
- **`schedule.start_day` / `stop_day`**:
  - Must be one of: `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday`.
  - In the default logic, Tuesday–Thursday are used for the weekly poll window.
- **`schedule.start_time` / `stop_time`**:
  - Format `HH:MM` (24-hour clock), e.g. `"12:00"`, `"20:00"`.
- **`schedule.timezone`**:
  - An [IANA timezone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones), e.g. `Europe/Berlin`, `America/New_York`.
- **`thread_id`** (optional):
  - Same meaning as `TELEGRAM_THREAD_ID` – if present here and in `vault.json`, the vault value takes precedence.

**Where the config is used in code**

- `vault.json` is read by `load_vault` in `bot.py`.
- `bot_config.json` is read by `load_bot_config` in `bot.py`, which populates:
  - `SURVEY_CONFIG` – question and options
  - `SCHEDULE_CONFIG` – start/stop days and times
  - `TIMEZONE` – used for all date/time logic

---

### 3. Running the Bot

You can run the bot **manually** in a terminal or set it up to run **automatically on system boot**.

#### 3.1. Create and activate a Python virtual environment

From inside the project directory:

##### Linux / macOS

```bash
# Install Python + venv support (if needed)
sudo apt update
sudo apt install -y python3 python3-venv python3-pip

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate
```

##### Windows (PowerShell)

```powershell
# Ensure Python is installed and in PATH
py --version

# Create and activate a virtual environment
py -m venv venv
.\venv\Scripts\Activate.ps1
```

#### 3.2. Install Python dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> If `requirements.txt` is missing, install the dependencies listed in your project’s README instead.

#### 3.3. Run the bot manually

With the virtual environment **activated** and configs in place:

```bash
python bot.py
```

- The bot will connect to Telegram and start polling for updates.
- In your target chat, send `/start` to **enable** automatic weekly survey management.
- Send `/stop` to temporarily disable it and `/status` to see current state.

To stop the bot manually, press `Ctrl+C` in the terminal.

---

### 3.4. Autostart on Linux (systemd)

This method keeps the bot running in the background and restarts it after reboots.

#### 3.4.1. Set up a dedicated install path and venv

Example (run as root or with `sudo`):

```bash
sudo mkdir -p /opt/Telegram_Weekly_Poll_Bot
sudo chown "$USER":"$USER" /opt/Telegram_Weekly_Poll_Bot
cd /opt/Telegram_Weekly_Poll_Bot

git clone https://github.com/<YOUR_GITHUB_USERNAME>/Telegram_Weekly_Poll_Bot.git .

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Ensure `vault.json` and `bot_config.json` are present and correctly configured in `/opt/Telegram_Weekly_Poll_Bot`.

#### 3.4.2. Install the systemd service unit

**Option A: Copy the unit from the project (recommended)**

The repository includes a ready-made unit file. From the project directory (e.g. `/opt/Telegram_Weekly_Poll_Bot`):

```bash
sudo cp /opt/Telegram_Weekly_Poll_Bot/telegram-bot-poll.service /etc/systemd/system/telegram-bot-poll.service
sudo systemctl daemon-reload
```

Adjust the first path if your bot lives elsewhere (e.g. `/root/Telegram_Weekly_Poll_Bot`). The unit file in the repo uses `/opt/Telegram_Weekly_Poll_Bot`; edit `/etc/systemd/system/telegram-bot-poll.service` if your path is different.

**Option B: Create the unit file manually**

Create `/etc/systemd/system/telegram-bot-poll.service`:

```bash
sudo nano /etc/systemd/system/telegram-bot-poll.service
```

Paste the following (adjust paths and `User` if needed):

```ini
[Unit]
Description=Telegram Weekly Poll Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/opt/Telegram_Weekly_Poll_Bot
Environment="PATH=/opt/Telegram_Weekly_Poll_Bot/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/Telegram_Weekly_Poll_Bot/venv/bin/python3 /opt/Telegram_Weekly_Poll_Bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Important notes:**

- Replace `User=botuser` with a real system user. Avoid `root` unless absolutely necessary.
- Make sure paths in `WorkingDirectory`, `Environment`, and `ExecStart` match your actual install location.

#### 3.4.3. Enable and start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now telegram-bot-poll.service

# Check status
sudo systemctl status telegram-bot-poll.service
```

If the status shows `active (running)`, the bot will:

- Start automatically on boot.
- Run continuously in the background.

---

### 3.5. Autostart on Windows (Task Scheduler)

On Windows, you can use **Task Scheduler** to start the bot at logon or on system startup.

#### 3.5.1. Prepare the environment

From PowerShell, inside the project directory:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Note the full paths:

- Project directory, e.g. `C:\Telegram_Weekly_Poll_Bot`
- Python executable, e.g. `C:\Telegram_Weekly_Poll_Bot\venv\Scripts\python.exe`

#### 3.5.2. Create a scheduled task (GUI)

1. Open **Task Scheduler**.
2. Click **Create Basic Task…**.
3. Name it, e.g. `TelegramWeeklyPollBot`.
4. **Trigger**: choose `When I log on` (or `At startup` if appropriate).
5. **Action**: `Start a program`:
   - **Program/script**: `C:\Telegram_Weekly_Poll_Bot\venv\Scripts\python.exe`
   - **Add arguments (optional)**: `C:\Telegram_Weekly_Poll_Bot\bot.py`
   - **Start in (optional)**: `C:\Telegram_Weekly_Poll_Bot`
6. Finish and confirm the task is created.

You can test it by right-clicking the task and selecting **Run**.

---

### 4. Stopping and Removing the Bot

This section explains how to:

- Stop the running bot.
- Disable autostart.
- Remove files and configuration.

#### 4.1. Linux – stop and disable the systemd service

Stop the running service:

```bash
sudo systemctl stop telegram-bot-poll.service
```

Prevent it from starting automatically:

```bash
sudo systemctl disable telegram-bot-poll.service
```

Optionally mask it to prevent manual starts:

```bash
sudo systemctl mask telegram-bot-poll.service
```

Check status:

```bash
systemctl status telegram-bot-poll.service
```

It should show as `inactive` or report that the unit could not be found.

#### 4.2. Linux – remove the systemd unit and project files

Remove the service unit file (only after you are sure about the path and name):

```bash
sudo rm /etc/systemd/system/telegram-bot-poll.service
sudo systemctl daemon-reload
```

Double-check the project directory before deleting:

```bash
ls -l /opt/Telegram_Weekly_Poll_Bot
```

If you are sure nothing else important is inside:

```bash
sudo rm -rf /opt/Telegram_Weekly_Poll_Bot
```

**Precaution:** Verify the directory path before using `rm -rf` to avoid accidental data loss.

#### 4.3. Windows – stop and disable the scheduled task

If the bot is running in a terminal you started:

- Close the window or press `Ctrl+C` in that terminal.

To disable or remove the Task Scheduler entry:

1. Open **Task Scheduler**.
2. Find your task (e.g. `TelegramWeeklyPollBot`) in **Task Scheduler Library**.
3. To stop it:
   - Right-click → **End**.
4. To disable autostart:
   - Right-click → **Disable**.
5. To remove it entirely:
   - Right-click → **Delete** and confirm.

Alternatively, from PowerShell (run as administrator):

```powershell
# Disable the task
Disable-ScheduledTask -TaskName "TelegramWeeklyPollBot"

# Remove the task completely
Unregister-ScheduledTask -TaskName "TelegramWeeklyPollBot" -Confirm:$false
```

#### 4.4. Windows – remove project files

Inspect the project folder first:

```powershell
Get-ChildItem "C:\Telegram_Weekly_Poll_Bot"
```

If you are sure you no longer need it:

```powershell
Remove-Item -Recurse -Force "C:\Telegram_Weekly_Poll_Bot"
```

---

### 5. Quick Reference

- **Clone project**:
  - `git clone https://github.com/<YOUR_GITHUB_USERNAME>/Telegram_Weekly_Poll_Bot.git`
- **Configure secrets**: edit `vault.json`.
- **Configure survey & schedule**: edit `bot_config.json`.
- **Create venv & install**:
  - `python3 -m venv venv && source venv/bin/activate`
  - `pip install -r requirements.txt`
- **Run manually**: `python bot.py`
- **Linux autostart**: create `/etc/systemd/system/telegram-bot-poll.service`, then `sudo systemctl enable --now telegram-bot-poll.service`.
- **Windows autostart**: create a Task Scheduler entry pointing to `venv\Scripts\python.exe bot.py`.
- **Remove (Linux)**: `systemctl stop/disable`, delete service file, then `rm -rf` the project directory.
- **Remove (Windows)**: disable/delete the scheduled task, then delete the project folder.

---

### 6. Troubleshooting

#### `telegram.error.TimedOut` or `httpcore.ConnectTimeout`

This means the server could not reach Telegram’s API (`api.telegram.org`) in time. Common causes:

- **Firewall or proxy** blocking outbound HTTPS (port 443) to Telegram.
- **DNS** not resolving `api.telegram.org`.
- **Network or ISP** restrictions (e.g. some datacentres or countries limit access to Telegram).

**Checks on the server:**

```bash
# Test connectivity and DNS
curl -v --connect-timeout 10 https://api.telegram.org

# If you use a proxy, configure it for the bot (see bot code / HTTPXRequest proxy options).
```

If `curl` also times out or fails, fix network/firewall/DNS or use a proxy before running the bot. The bot is configured with 30-second connect/read/write timeouts; if the network is very slow or blocked, increase them in `bot.py` or ensure the server can reach Telegram.

#### Bot does not respond to commands (/start, /stop, /status)

If the bot runs without errors but does not reply to commands in Telegram:

1. **Only one instance**  
   Ensure a single process is running. Multiple processes with the same token share updates; only one will receive each update.
   ```bash
   pgrep -af "bot.py"
   ```
   If you see more than one line, stop the extra process(es) (e.g. `kill <PID>` or `systemctl stop ...`).

2. **Bot is in the chat**  
   - **Groups**: Add the bot to the group (Invite → search by bot username).  
   - **Private chat**: Open the bot in Telegram and tap **Start** (or send `/start`) so the conversation exists.

3. **Same bot and token**  
   The token in `vault.json` must belong to the bot you are messaging. Check with [@BotFather](https://t.me/BotFather): `/mybots` → select the bot → API Token. It must match `TELEGRAM_BOT_TOKEN` exactly (no extra spaces or quotes inside the string).

4. **Test in private chat first**  
   Send `/start` in a **private chat** with the bot. If it replies there but not in a group, the group likely has **Privacy Mode** enabled: in BotFather → Bot Settings → Group Privacy, turn it **Off** so the bot receives all messages in groups, or ensure commands are sent in a form the bot receives (e.g. `/start` at the start of the message).

5. **Confirm the process is polling**  
   After starting the bot, it should run without exiting. If it exits immediately, check the traceback. If it runs but never receives updates, run a connectivity check (see “Timed out” above) and ensure no firewall blocks outbound HTTPS to `api.telegram.org`.

6. **Temporary logging (optional)**  
   To see whether updates and handlers run, you can temporarily enable logging in `bot.py` before `application.add_error_handler(...)`:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   logging.getLogger("telegram").setLevel(logging.INFO)
   ```
   Restart the bot, send a command, and watch the terminal for incoming updates and any handler errors. Remove or comment out these lines when done.

#### Stopping and restarting the bot

- **Running manually in a terminal**  
  **Ctrl+C** is the correct way to stop. The bot catches the interrupt and shuts down the updater and connection cleanly. To restart, run `python bot.py` again in the same (or a new) terminal with the venv activated.

- **Running as a systemd service**  
  Stop: `sudo systemctl stop telegram-bot-poll.service`  
  Start: `sudo systemctl start telegram-bot-poll.service`  
  Restart: `sudo systemctl restart telegram-bot-poll.service`  
  Do not rely on Ctrl+C when the bot is in the background; use `systemctl` so the service state stays correct.  
  If you see **Unit telegram-bot-poll.service not found**, install the service file first (see **§3.4.2**): copy `telegram-bot-poll.service` to `/etc/systemd/system/`, then run `sudo systemctl daemon-reload` before starting.
