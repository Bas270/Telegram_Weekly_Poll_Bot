import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, time, timedelta
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
BOT_CONFIG_PATH = BASE_DIR / "bot_config.json"


# ================== CONFIG MODELS ==================

DAY_NAME_TO_INT = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


@dataclass
class SurveyConfig:
    """Survey content configuration."""
    title: str
    options: list[str]


@dataclass
class ScheduleConfig:
    """Scheduling parameters."""
    start_weekday: int  # 0 = Monday ... 6 = Sunday
    start_hour: int
    start_minute: int
    stop_weekday: int
    stop_hour: int
    stop_minute: int
    timezone: ZoneInfo


@dataclass
class BotConfig:
    """Complete bot configuration."""
    survey: SurveyConfig
    schedule: ScheduleConfig


# ================== CONFIG LOADING FUNCTIONS ==================

def load_vault(path: Path) -> tuple[str, int]:
    """
    Load secrets (bot token, chat id) from vault.json.

    vault.json schema:
    {
      "TELEGRAM_BOT_TOKEN": "...",
      "TELEGRAM_TARGET_CHAT_ID": "-1001234567890"
    }
    """
    if not path.exists():
        raise RuntimeError(f"Vault file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in vault file: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Error reading vault file: {e}") from e

    token = data.get("TELEGRAM_BOT_TOKEN")
    chat_id = data.get("TELEGRAM_TARGET_CHAT_ID")

    if not token or not chat_id:
        raise RuntimeError(
            "Vault file must contain TELEGRAM_BOT_TOKEN and TELEGRAM_TARGET_CHAT_ID"
        )

    return token, int(chat_id)


def _parse_day(name: str) -> int:
    """Parse day name to weekday integer (0=Monday, 6=Sunday)."""
    try:
        return DAY_NAME_TO_INT[name.strip().lower()]
    except (KeyError, AttributeError) as e:
        valid = ", ".join(d.capitalize() for d in DAY_NAME_TO_INT.keys())
        raise ValueError(f"Invalid day name '{name}'. Must be one of: {valid}") from e


def _parse_hhmm(hhmm: str) -> tuple[int, int]:
    """Parse HH:MM time string to (hour, minute) tuple."""
    try:
        h_str, m_str = hhmm.split(":", 1)
        h, m = int(h_str), int(m_str)
    except ValueError as e:
        raise ValueError(f"Invalid time format '{hhmm}'. Expected 'HH:MM'.") from e

    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError(f"Invalid time '{hhmm}'. Hour must be 0-23, minute must be 0-59.")
    return h, m


def load_bot_config(path: Path) -> BotConfig:
    """
    Load complete bot configuration from bot_config.json.

    bot_config.json schema:
    {
      "survey": {
        "title": "Survey question text",
        "options": ["Option 1", "Option 2", ...]
      },
      "schedule": {
        "start_day": "Tuesday",
        "start_time": "12:00",
        "stop_day": "Thursday",
        "stop_time": "20:00",
        "timezone": "Europe/Berlin"
      }
    }
    """
    if not path.exists():
        raise RuntimeError(f"Bot config file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in bot config file: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Error reading bot config file: {e}") from e

    # Validate and parse survey section
    survey_raw = raw.get("survey")
    if not survey_raw:
        raise ValueError("bot_config.json must contain 'survey' section")
    
    survey_title = survey_raw.get("title")
    survey_options = survey_raw.get("options", [])

    if not survey_title or not isinstance(survey_title, str):
        raise ValueError("bot_config.json: 'survey.title' must be a non-empty string")
    
    if not isinstance(survey_options, list):
        raise ValueError("bot_config.json: 'survey.options' must be a list")
    
    if len(survey_options) < 2:
        raise ValueError("bot_config.json: 'survey.options' must contain at least 2 options")
    
    if len(survey_options) > 10:
        raise ValueError("bot_config.json: 'survey.options' must contain at most 10 options")
    
    # Validate all options are strings
    for i, option in enumerate(survey_options):
        if not isinstance(option, str) or not option.strip():
            raise ValueError(f"bot_config.json: 'survey.options[{i}]' must be a non-empty string")

    survey_config = SurveyConfig(
        title=survey_title.strip(),
        options=[opt.strip() for opt in survey_options],
    )

    # Validate and parse schedule section
    schedule_raw = raw.get("schedule")
    if not schedule_raw:
        raise ValueError("bot_config.json must contain 'schedule' section")

    start_day = schedule_raw.get("start_day")
    start_time = schedule_raw.get("start_time")
    stop_day = schedule_raw.get("stop_day")
    stop_time = schedule_raw.get("stop_time")
    tz_name = schedule_raw.get("timezone", "Europe/Berlin")

    if not start_day or not start_time or not stop_day or not stop_time:
        raise ValueError(
            "bot_config.json: 'schedule' section must define 'start_day', 'start_time', "
            "'stop_day', and 'stop_time'"
        )

    try:
        start_weekday = _parse_day(start_day)
        stop_weekday = _parse_day(stop_day)
        start_hour, start_minute = _parse_hhmm(start_time)
        stop_hour, stop_minute = _parse_hhmm(stop_time)
    except ValueError as e:
        raise ValueError(f"bot_config.json: Invalid schedule format - {e}") from e

    try:
        tz = ZoneInfo(tz_name)
    except Exception as e:
        raise ValueError(f"bot_config.json: Invalid timezone '{tz_name}': {e}") from e

    schedule_config = ScheduleConfig(
        start_weekday=start_weekday,
        start_hour=start_hour,
        start_minute=start_minute,
        stop_weekday=stop_weekday,
        stop_hour=stop_hour,
        stop_minute=stop_minute,
        timezone=tz,
    )

    return BotConfig(survey=survey_config, schedule=schedule_config)


# ================== LOAD CONFIGURATION ==================

try:
    TELEGRAM_BOT_TOKEN, TARGET_CHAT_ID = load_vault(VAULT_PATH)
    BOT_CONFIG = load_bot_config(BOT_CONFIG_PATH)
    SURVEY_CONFIG = BOT_CONFIG.survey
    SCHEDULE_CONFIG = BOT_CONFIG.schedule
    TIMEZONE = SCHEDULE_CONFIG.timezone
except Exception as e:
    logging.basicConfig(level=logging.ERROR)
    logging.error(f"Failed to load configuration: {e}")
    raise


# ================== LOGGING ==================

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ================== HELPERS ==================

def _next_weekday_time(
    now: datetime,
    target_weekday: int,
    hour: int,
    minute: int,
) -> datetime:
    """
    Given 'now', return the next datetime with weekday=target_weekday and the
    given hour/minute in the same timezone. If that datetime is <= now,
    jump one week ahead.
    """
    days_ahead = (target_weekday - now.weekday()) % 7
    candidate = (now + timedelta(days=days_ahead)).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )
    if candidate <= now:
        candidate += timedelta(days=7)
    return candidate


# ================== HANDLERS & JOBS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Simple /start command: shows chat id and current schedule."""
    chat = update.effective_chat
    text = (
        "Hi, I'm the weekly poll bot.\n"
        f"This chat id is: {chat.id}\n\n"
        "Current schedule (from bot_config.json):\n"
        f"- Start: {list(DAY_NAME_TO_INT.keys())[SCHEDULE_CONFIG.start_weekday].capitalize()} "
        f"{SCHEDULE_CONFIG.start_hour:02d}:{SCHEDULE_CONFIG.start_minute:02d}\n"
        f"- Stop:  {list(DAY_NAME_TO_INT.keys())[SCHEDULE_CONFIG.stop_weekday].capitalize()} "
        f"{SCHEDULE_CONFIG.stop_hour:02d}:{SCHEDULE_CONFIG.stop_minute:02d}\n"
        f"- Timezone: {TIMEZONE}\n\n"
        f"Survey title: {SURVEY_CONFIG.title}\n"
        f"Options: {', '.join(SURVEY_CONFIG.options)}"
    )
    await update.message.reply_text(text)


async def publish_poll(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Job: publish the weekly poll at the configured start day/time.
    Also schedules a job to close this specific poll at the configured stop
    day/time of the same poll week.
    """
    bot = context.bot
    chat_id = TARGET_CHAT_ID

    try:
        logger.info(
            "Publishing weekly poll to chat %s at %s",
            chat_id,
            datetime.now(TIMEZONE).isoformat(),
        )
        message = await bot.send_poll(
            chat_id=chat_id,
            question=SURVEY_CONFIG.title,
            options=SURVEY_CONFIG.options,
            is_anonymous=False,            # non-anonymous
            allows_multiple_answers=True,  # multi-select per user
            type=Poll.REGULAR,
        )
    except TelegramError as e:
        logger.exception("Failed to send poll: %s", e)
        return
    except Exception as e:
        logger.exception("Unexpected error while sending poll: %s", e)
        return

    # Compute when to close the poll based on schedule config
    now = datetime.now(TIMEZONE)
    stop_at = _next_weekday_time(
        now=now,
        target_weekday=SCHEDULE_CONFIG.stop_weekday,
        hour=SCHEDULE_CONFIG.stop_hour,
        minute=SCHEDULE_CONFIG.stop_minute,
    )
    delay = (stop_at - now).total_seconds()

    if delay <= 0:
        logger.warning(
            "Computed non-positive delay (%s) for close_poll; skipping schedule.",
            delay,
        )
        return

    logger.info(
        "Scheduling close_poll for message %s at %s (in %.0f seconds)",
        message.message_id,
        stop_at.isoformat(),
        delay,
    )

    context.job_queue.run_once(
        close_poll,
        when=delay,
        data={
            "chat_id": chat_id,
            "message_id": message.message_id,
            "poll_id": message.poll.id,
        },
        name=f"close_poll_{message.message_id}",
    )


async def close_poll(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Job: close a previously published poll."""
    data = context.job.data or {}
    chat_id = data.get("chat_id")
    message_id = data.get("message_id")

    if chat_id is None or message_id is None:
        logger.error("close_poll job missing chat_id or message_id in job data.")
        return

    try:
        logger.info(
            "Closing poll in chat %s (message %s) at %s",
            chat_id,
            message_id,
            datetime.now(TIMEZONE).isoformat(),
        )
        await context.bot.stop_poll(chat_id=chat_id, message_id=message_id)
    except TelegramError as e:
        logger.exception("Failed to close poll: %s", e)
    except Exception as e:
        logger.exception("Unexpected error while closing poll: %s", e)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error logger for updates and jobs."""
    logger.error("Exception while handling an update/job", exc_info=context.error)


# ================== MAIN (ASYNC) ==================

async def main() -> None:
    """
    Build the application, register handlers, and start polling.

    The survey content and schedule are entirely driven by bot_config.json.
    """
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    # Handlers
    application.add_handler(CommandHandler("start", start))

    application.add_error_handler(error_handler)

    job_queue = application.job_queue

    # Schedule the weekly poll according to config
    job_queue.run_daily(
        callback=publish_poll,
        time=time(
            hour=SCHEDULE_CONFIG.start_hour,
            minute=SCHEDULE_CONFIG.start_minute,
            tzinfo=TIMEZONE,
        ),
        days=(SCHEDULE_CONFIG.start_weekday,),
        name="publish_scheduled_poll",
    )

    logger.info(
        "Starting bot with configuration from bot_config.json:"
    )
    logger.info(
        "  Schedule: start_day=%s %02d:%02d, stop_day=%s %02d:%02d, tz=%s",
        list(DAY_NAME_TO_INT.keys())[SCHEDULE_CONFIG.start_weekday].capitalize(),
        SCHEDULE_CONFIG.start_hour,
        SCHEDULE_CONFIG.start_minute,
        list(DAY_NAME_TO_INT.keys())[SCHEDULE_CONFIG.stop_weekday].capitalize(),
        SCHEDULE_CONFIG.stop_hour,
        SCHEDULE_CONFIG.stop_minute,
        TIMEZONE,
    )
    logger.info(
        "  Survey: title='%s', options=%s",
        SURVEY_CONFIG.title,
        SURVEY_CONFIG.options,
    )

    # Manual lifecycle (no run_polling)
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
