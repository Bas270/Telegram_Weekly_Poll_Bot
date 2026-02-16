import os
import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from telegram import Update, Poll
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# ================== PATHS ==================

BASE_DIR = Path(__file__).resolve().parent
VAULT_PATH = BASE_DIR / "vault.json"
SURVEY_CONFIG_PATH = BASE_DIR / "survey_config.json"


# ================== CONFIG MODELS ==================

@dataclass
class SurveyConfig:
    """Holds survey settings loaded from survey_config.json."""
    title: str
    options: list[str]
    start: datetime
    end: datetime
    timezone: ZoneInfo


def load_vault(path: Path) -> tuple[str, int]:
    """
    Load sensitive data (bot token, chat id) from vault.json.

    vault.json schema:
    {
      "TELEGRAM_BOT_TOKEN": "...",
      "TELEGRAM_TARGET_CHAT_ID": "-1001234567890"
    }
    """
    if not path.exists():
        raise RuntimeError(f"Vault file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    token = data.get("TELEGRAM_BOT_TOKEN")
    chat_id = data.get("TELEGRAM_TARGET_CHAT_ID")

    if not token or not chat_id:
        raise RuntimeError(
            "Vault file must contain TELEGRAM_BOT_TOKEN and TELEGRAM_TARGET_CHAT_ID"
        )

    return token, int(chat_id)


def load_survey_config(path: Path) -> SurveyConfig:
    """
    Load survey settings from survey_config.json.

    survey_config.json schema:
    {
      "title": "...",
      "options": ["...", "..."],
      "start": "2026-02-16T12:00:00",
      "end": "2026-02-18T20:00:00",
      "timezone": "Europe/Berlin"
    }
    """
    if not path.exists():
        raise RuntimeError(f"Survey config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    title = raw.get("title")
    options = raw.get("options", [])
    start_str = raw.get("start")
    end_str = raw.get("end")
    tz_name = raw.get("timezone", "Europe/Berlin")

    if not title:
        raise ValueError("survey_config.json: 'title' is required")
    if not isinstance(options, list) or not (1 <= len(options) <= 10):
        raise ValueError("survey_config.json: 'options' must be a list with 1–10 items")
    if not start_str or not end_str:
        raise ValueError("survey_config.json: 'start' and 'end' are required")

    tz = ZoneInfo(tz_name)

    # Accept ISO 8601 strings, with or without timezone; if naive, assume tz
    start = datetime.fromisoformat(start_str)
    if start.tzinfo is None:
        start = start.replace(tzinfo=tz)

    end = datetime.fromisoformat(end_str)
    if end.tzinfo is None:
        end = end.replace(tzinfo=tz)

    return SurveyConfig(
        title=title,
        options=options,
        start=start,
        end=end,
        timezone=tz,
    )


# ================== LOAD CONFIG & VAULT ==================

TELEGRAM_BOT_TOKEN, TARGET_CHAT_ID = load_vault(VAULT_PATH)
SURVEY_CONFIG = load_survey_config(SURVEY_CONFIG_PATH)
TIMEZONE = SURVEY_CONFIG.timezone  # single source of truth for TZ

# ================== LOGGING ==================

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ================== HANDLERS & DEBUG JOBS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simple /start command: shows chat id and config info."""
    chat = update.effective_chat
    text = (
        "Hi, I'm the weekly poll bot (DEBUG MODE).\n"
        f"This chat id is: {chat.id}\n\n"
        f"Configured survey title:\n- {SURVEY_CONFIG.title}\n\n"
        f"Configured start: {SURVEY_CONFIG.start.isoformat()}\n"
        f"Configured end:   {SURVEY_CONFIG.end.isoformat()}\n\n"
        "In debug mode, polls are triggered by /status:\n"
        "- Send poll 30s after /status\n"
        "- Close poll 90s after /status"
    )
    await update.message.reply_text(text)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Debug command: schedule poll 30s from now, close 90s from now.

    This uses SURVEY_CONFIG for the poll title and options, but timing is
    relative to when /status is received.
    """
    chat_id = update.effective_chat.id
    now = datetime.now(TIMEZONE)

    start_delay = 30  # seconds until poll is sent
    stop_delay = 90   # seconds until poll is closed (from now)

    start_at = now + timedelta(seconds=start_delay)
    stop_at = now + timedelta(seconds=stop_delay)

    logger.info(
        "DEBUG: /status received at %s (chat_id=%s). "
        "Scheduling poll send at %s (+%ss) and close at %s (+%ss).",
        now.isoformat(),
        chat_id,
        start_at.isoformat(),
        start_delay,
        stop_at.isoformat(),
        stop_delay,
    )

    # Schedule sending the poll 30s from now
    context.job_queue.run_once(
        send_debug_poll,
        when=start_delay,
        data={"chat_id": chat_id},
        name=f"debug_send_{chat_id}_{int(now.timestamp())}",
    )

    await update.message.reply_text(
        "DEBUG: Poll scheduled from configuration.\n"
        f"- Now: {now.isoformat()}\n"
        f"- Will send at: {start_at.isoformat()} (in {start_delay}s)\n"
        f"- Will close at: {stop_at.isoformat()} (in {stop_delay}s)\n\n"
        f"Survey title: {SURVEY_CONFIG.title}\n"
        f"Options: {', '.join(SURVEY_CONFIG.options)}"
    )


async def send_debug_poll(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send a poll ~30s after /status, using config title/options,
    then schedule close ~60s later (total 90s from /status).
    """
    bot = context.bot
    data = context.job.data or {}
    chat_id = data.get("chat_id", TARGET_CHAT_ID)

    now = datetime.now(TIMEZONE)
    logger.info("DEBUG: Sending poll at %s (chat_id=%s)", now.isoformat(), chat_id)

    try:
        message = await bot.send_poll(
            chat_id=chat_id,
            question=SURVEY_CONFIG.title,
            options=SURVEY_CONFIG.options,
            is_anonymous=False,            # non-anonymous
            allows_multiple_answers=True,  # multi-select
            type=Poll.REGULAR,
        )
    except TelegramError as e:
        logger.exception("DEBUG: Failed to send debug poll: %s", e)
        return
    except Exception as e:
        logger.exception("DEBUG: Unexpected error while sending debug poll: %s", e)
        return

    # Schedule closing 60s after sending => 90s after /status (30 + 60)
    close_in = 60
    close_at = datetime.now(TIMEZONE) + timedelta(seconds=close_in)
    logger.info(
        "DEBUG: Scheduling poll close for message_id=%s at %s (in %s seconds)",
        message.message_id,
        close_at.isoformat(),
        close_in,
    )

    context.job_queue.run_once(
        close_debug_poll,
        when=close_in,
        data={"chat_id": chat_id, "message_id": message.message_id},
        name=f"debug_close_{message.message_id}",
    )


async def close_debug_poll(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Close the debug poll and log exact timestamp."""
    data = context.job.data or {}
    chat_id = data.get("chat_id")
    message_id = data.get("message_id")

    now = datetime.now(TIMEZONE)
    logger.info(
        "DEBUG: Attempting to close poll at %s (chat_id=%s, message_id=%s)",
        now.isoformat(),
        chat_id,
        message_id,
    )

    if chat_id is None or message_id is None:
        logger.error("DEBUG: close_debug_poll missing chat_id or message_id.")
        return

    try:
        await context.bot.stop_poll(chat_id=chat_id, message_id=message_id)
        logger.info(
            "DEBUG: Successfully closed poll at %s (chat_id=%s, message_id=%s)",
            datetime.now(TIMEZONE).isoformat(),
            chat_id,
            message_id,
        )
    except TelegramError as e:
        logger.exception("DEBUG: Failed to close debug poll: %s", e)
    except Exception as e:
        logger.exception("DEBUG: Unexpected error while closing debug poll: %s", e)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error logger for updates and jobs."""
    logger.error("Exception while handling an update/job", exc_info=context.error)


# ================== MAIN (ASYNC) ==================

async def main() -> None:
    """
    Build the application, register handlers, and start polling in debug mode.

    In production, you would use SURVEY_CONFIG.start/end to schedule real
    weekly jobs; here we just verify scheduling via /status and logs.
    """
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))  # DEBUG trigger

    application.add_error_handler(error_handler)

    job_queue = application.job_queue

    # No fixed weekly schedule in DEBUG mode:
    # In a production version, you'd use SURVEY_CONFIG.start/end here.

    logger.info(
        "DEBUG MODE: Config loaded. "
        "Polls are triggered via /status (30s start, 90s stop)."
    )
    logger.info(
        "CONFIG SUMMARY: title='%s', options=%s, start=%s, end=%s, tz=%s",
        SURVEY_CONFIG.title,
        SURVEY_CONFIG.options,
        SURVEY_CONFIG.start.isoformat(),
        SURVEY_CONFIG.end.isoformat(),
        SURVEY_CONFIG.timezone,
    )

    # Manual lifecycle (no run_polling / wait_for_stop)
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    stop_event = asyncio.Event()
    try:
        # Block here until Ctrl+C cancels asyncio.run(main())
        await stop_event.wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Shutdown signal received, stopping bot...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())