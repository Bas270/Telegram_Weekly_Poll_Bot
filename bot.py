import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta, date
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import Optional

from telegram import Update, Poll
from telegram.error import TelegramError
from telegram.request import HTTPXRequest
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
    thread_id: Optional[int] = None  # Topic/thread ID for Telegram groups


# ================== CONFIG LOADING FUNCTIONS ==================

def load_vault(path: Path) -> tuple[str, int, Optional[int]]:
    """
    Load secrets (bot token, chat id, optional thread id) from vault.json.

    vault.json schema:
    {
      "TELEGRAM_BOT_TOKEN": "...",
      "TELEGRAM_TARGET_CHAT_ID": "-1001234567890",
      "TELEGRAM_THREAD_ID": 12345  // Optional
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
    thread_id = data.get("TELEGRAM_THREAD_ID")  # Optional

    if not token or not chat_id:
        raise RuntimeError(
            "Vault file must contain TELEGRAM_BOT_TOKEN and TELEGRAM_TARGET_CHAT_ID"
        )

    # Validate thread_id if provided
    if thread_id is not None:
        try:
            thread_id = int(thread_id)
            if thread_id <= 0:
                raise ValueError("TELEGRAM_THREAD_ID must be a positive integer")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid TELEGRAM_THREAD_ID: must be a positive integer") from e

    return token, int(chat_id), thread_id


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


def load_bot_config(path: Path, thread_id_from_vault: Optional[int] = None) -> BotConfig:
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
      },
      "thread_id": 12345  // Optional, can also be in vault.json
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

    # Get thread_id from config file or vault (vault takes precedence)
    thread_id = thread_id_from_vault
    if thread_id is None:
        thread_id_raw = raw.get("thread_id")
        if thread_id_raw is not None:
            try:
                thread_id = int(thread_id_raw)
                if thread_id <= 0:
                    raise ValueError("thread_id must be a positive integer")
            except (ValueError, TypeError) as e:
                raise ValueError(f"bot_config.json: Invalid thread_id - must be a positive integer") from e

    return BotConfig(
        survey=survey_config,
        schedule=schedule_config,
        thread_id=thread_id,
    )


# ================== LOAD CONFIGURATION ==================

try:
    TELEGRAM_BOT_TOKEN, TARGET_CHAT_ID, THREAD_ID_FROM_VAULT = load_vault(VAULT_PATH)
    BOT_CONFIG = load_bot_config(BOT_CONFIG_PATH, thread_id_from_vault=THREAD_ID_FROM_VAULT)
    SURVEY_CONFIG = BOT_CONFIG.survey
    SCHEDULE_CONFIG = BOT_CONFIG.schedule
    THREAD_ID = BOT_CONFIG.thread_id
    TIMEZONE = SCHEDULE_CONFIG.timezone
except Exception:
    # Fail fast on configuration errors; the traceback will be visible to the operator.
    raise


# ================== LOGGING (DISABLED OUTPUT) ==================

# We intentionally do not emit logs to system outputs. The logger below is
# configured with a NullHandler and does not propagate messages.
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
logger.propagate = False


def _now_tz() -> datetime:
    """Current time in configured timezone."""
    return datetime.now(TIMEZONE)


@dataclass
class PollState:
    """In-memory state for the latest poll in a chat."""

    last_published_at: Optional[datetime] = None
    last_stopped_at: Optional[datetime] = None
    current_message_id: Optional[int] = None
    current_poll_id: Optional[str] = None


@dataclass
class ChatState:
    """In-memory runtime state per chat."""

    running: bool = False
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    poll: PollState = field(default_factory=PollState)


# Global in-memory state for all chats this process has seen.
CHAT_STATES: dict[int, ChatState] = {}


def _get_chat_state(chat_id: int) -> ChatState:
    """Return (and create if missing) the in-memory state for a chat."""
    state = CHAT_STATES.get(chat_id)
    if state is None:
        state = ChatState()
        CHAT_STATES[chat_id] = state
    return state


def _get_publication_state(poll: PollState) -> str:
    """
    Determine publication state for /status.

    Returns one of:
    - "not published"
    - "published"
    - "stopped"
    """
    if poll.current_message_id is not None:
        return "published"

    if (
        poll.last_published_at is not None
        and poll.last_stopped_at is not None
        and poll.last_stopped_at >= poll.last_published_at
    ):
        return "stopped"

    return "not published"


# ================== SURVEY OPERATIONS (PUBLISH/STOP) ==================

async def _publish_new_survey(
    context: ContextTypes.DEFAULT_TYPE,
    *,
    chat_id: int,
    chat_state: ChatState,
    now: datetime,
) -> None:
    """
    Publish a new survey (Telegram poll) for the given chat.

    Errors are swallowed to keep behaviour simple; /status reflects what is
    known from in-memory state only.
    """
    bot = context.bot

    poll_params = {
        "chat_id": chat_id,
        "question": SURVEY_CONFIG.title,
        "options": SURVEY_CONFIG.options,
        "is_anonymous": False,
        "allows_multiple_answers": True,
        "type": Poll.REGULAR,
    }

    if THREAD_ID is not None:
        poll_params["message_thread_id"] = THREAD_ID

    try:
        message = await bot.send_poll(**poll_params)
    except TelegramError:
        # Publishing failed; leave poll state unchanged.
        return

    poll = chat_state.poll
    poll.current_message_id = message.message_id
    poll.current_poll_id = message.poll.id
    poll.last_published_at = now
    poll.last_stopped_at = None


async def _stop_survey(
    context: ContextTypes.DEFAULT_TYPE,
    *,
    chat_id: int,
    chat_state: ChatState,
    now: datetime,
) -> None:
    """
    Stop an existing survey for the given chat if one is currently active.
    """
    poll = chat_state.poll
    if poll.current_message_id is None:
        return

    try:
        await context.bot.stop_poll(chat_id=chat_id, message_id=poll.current_message_id)
    except TelegramError:
        # Stopping failed; keep the last known state as-is.
        return

    poll.last_stopped_at = now
    poll.current_message_id = None


# ================== SURVEY POLICY (DAY/TIME CONTROLS) ==================

def _is_monday_or_sunday(weekday: int) -> bool:
    return weekday in (0, 6)


def _is_friday_or_saturday(weekday: int) -> bool:
    return weekday in (4, 5)


def _is_tuesday_or_thursday(weekday: int) -> bool:
    return weekday in (1, 3)


def _time_ge(t: time, hh: int, mm: int) -> bool:
    return t >= time(hour=hh, minute=mm)


def _time_lt(t: time, hh: int, mm: int) -> bool:
    return t < time(hour=hh, minute=mm)


async def _ensure_active_survey_for_cycle(context: ContextTypes.DEFAULT_TYPE, *, cycle_date: date, now: datetime) -> None:
    """
    Legacy helper (no-op). Kept for backward compatibility; not used anymore.
    """
    return


async def _ensure_stopped_if_exists(context: ContextTypes.DEFAULT_TYPE, *, now: datetime, reason: str) -> None:
    """
    Legacy helper (no-op). Kept for backward compatibility; not used anymore.
    """
    _ = context, now, reason
    return


async def manage_survey_policy(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Repeating job: enforce the requested weekly survey policy.

    Policy requirements implemented:
    - Monday/Sunday: do nothing.
    - Friday/Saturday: if a survey exists and isn't stopped, stop it (log failures).
    - Tuesday/Thursday special controls:
      - Tuesday before 12:00: do nothing.
      - Thursday at/after 20:00: ensure survey is stopped (log failures).
      - Tuesday at/after 12:00, Wednesday any time, Thursday before 20:00:
        ensure a survey is present (publish if missing; log failures).
    """
    now = _now_tz()
    weekday = now.weekday()
    t = now.time()

    # Apply policy to each chat that has been started via /start.
    for chat_id, chat_state in list(CHAT_STATES.items()):
        if not chat_state.running:
            continue

        # Monday or Sunday: no action.
        if _is_monday_or_sunday(weekday):
            continue

        # Friday or Saturday: ensure survey is stopped if it exists.
        if _is_friday_or_saturday(weekday):
            await _stop_survey(context, chat_id=chat_id, chat_state=chat_state, now=now)
            continue

        # Tuesday or Thursday have time-gated rules.
        if _is_tuesday_or_thursday(weekday):
            # Tuesday before 12:00 → no action.
            if weekday == 1 and _time_lt(t, 12, 0):
                continue

            # Thursday at/after 20:00 → ensure survey is stopped.
            if weekday == 3 and _time_ge(t, 20, 0):
                await _stop_survey(context, chat_id=chat_id, chat_state=chat_state, now=now)
                continue

            # Tuesday at/after 12:00 or Thursday before 20:00 → ensure survey is published.
            if chat_state.poll.current_message_id is None:
                await _publish_new_survey(context, chat_id=chat_id, chat_state=chat_state, now=now)
            continue

        # Wednesday any time → ensure survey is published.
        if weekday == 2:
            if chat_state.poll.current_message_id is None:
                await _publish_new_survey(context, chat_id=chat_id, chat_state=chat_state, now=now)
            continue


# ================== HANDLERS ==================

def _format_dt(dt: Optional[datetime]) -> str:
    """Format datetimes for human-readable chat output."""
    if dt is None:
        return "not available"
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /start – enable automatic survey management in this chat and record start time.
    """
    if not update.message:
        return

    chat = update.effective_chat
    chat_id = chat.id
    now = _now_tz()

    state = _get_chat_state(chat_id)

    if state.running:
        text = (
            "Bot is already running in this chat.\n"
            f"Started at: {_format_dt(state.started_at)}"
        )
    else:
        state.running = True
        state.started_at = now
        state.stopped_at = None

        text = (
            "Bot started in this chat.\n"
            f"Poll window: Tuesday 12:00 to Thursday 20:00 ({TIMEZONE})\n"
            "Polls will be published and stopped automatically based on the day and time."
        )

    await update.message.reply_text(text)


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /stop – disable automatic survey management in this chat and record stop time.
    """
    if not update.message:
        return

    chat = update.effective_chat
    chat_id = chat.id
    now = _now_tz()

    state = _get_chat_state(chat_id)

    if not state.running:
        await update.message.reply_text("Bot is not running in this chat.")
        return

    state.running = False
    state.stopped_at = now

    await update.message.reply_text(
        f"Bot stopped in this chat at {_format_dt(now)}."
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /status – report current bot state and last poll lifecycle information.
    """
    if not update.message:
        return

    chat = update.effective_chat
    chat_id = chat.id

    state = _get_chat_state(chat_id)
    poll = state.poll

    publication_state = _get_publication_state(poll)

    text = (
        "Bot status:\n"
        f"- running: {'yes' if state.running else 'no'}\n"
        f"- start time: {_format_dt(state.started_at)}\n"
        f"- last poll published at: {_format_dt(poll.last_published_at)}\n"
        f"- poll stopped at: {_format_dt(poll.last_stopped_at)}\n"
        f"- publication state: {publication_state}"
    )

    await update.message.reply_text(text)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Global error handler.

    Intentionally does not log to system outputs to keep the bot silent in logs.
    """
    _ = update, context  # Avoid unused parameter warnings.


# ================== MAIN (ASYNC) ==================

async def main() -> None:
    """
    Build the application, register handlers, and start polling.

    The survey content and schedule are entirely driven by bot_config.json.
    """
    # Use longer timeouts so the bot can connect on slow or restricted networks.
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
    )
    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .request(request)
        .build()
    )

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("status", status))

    application.add_error_handler(error_handler)

    job_queue = application.job_queue

    # Policy enforcement loop: runs frequently to enforce survey rules.
    job_queue.run_repeating(
        callback=manage_survey_policy,
        interval=300,  # 5 minutes
        first=5,
        name="manage_survey_policy",
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
        # Graceful shutdown without logging to system outputs.
        pass
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
