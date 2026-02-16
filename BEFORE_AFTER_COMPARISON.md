# Before/After Comparison

## Configuration Files

### BEFORE: `schedule_config.json`
```json
{
  "start_day": "Tuesday",
  "start_time": "12:00",
  "stop_day": "Thursday",
  "stop_time": "20:00",
  "timezone": "Europe/Berlin"
}
```

### AFTER: `bot_config.json`
```json
{
  "survey": {
    "title": "Weekly check-in: how are you planning to contribute this week?",
    "options": [
      "Code review",
      "New feature development",
      "Bug fixing",
      "Writing documentation",
      "Testing / QA",
      "Planning / meetings"
    ]
  },
  "schedule": {
    "start_day": "Tuesday",
    "start_time": "12:00",
    "stop_day": "Thursday",
    "stop_time": "20:00",
    "timezone": "Europe/Berlin"
  }
}
```

---

## Code Changes

### BEFORE: Hardcoded Survey Content

```python
# ================== SURVEY CONTENT ==================

POLL_QUESTION = "Weekly check-in: how are you planning to contribute this week?"
POLL_OPTIONS = [
    "Code review",
    "New feature development",
    "Bug fixing",
    "Writing documentation",
    "Testing / QA",
    "Planning / meetings",
]

# Usage in publish_poll():
message = await bot.send_poll(
    chat_id=chat_id,
    question=POLL_QUESTION,
    options=POLL_OPTIONS,
    ...
)
```

### AFTER: Loaded from Configuration

```python
# Survey content loaded from bot_config.json
SURVEY_CONFIG = BOT_CONFIG.survey

# Usage in publish_poll():
message = await bot.send_poll(
    chat_id=chat_id,
    question=SURVEY_CONFIG.title,
    options=SURVEY_CONFIG.options,
    ...
)
```

---

## Configuration Loading

### BEFORE

```python
SCHEDULE_CONFIG_PATH = BASE_DIR / "schedule_config.json"
SCHEDULE_CONFIG = load_schedule_config(SCHEDULE_CONFIG_PATH)
```

### AFTER

```python
BOT_CONFIG_PATH = BASE_DIR / "bot_config.json"
BOT_CONFIG = load_bot_config(BOT_CONFIG_PATH)
SURVEY_CONFIG = BOT_CONFIG.survey
SCHEDULE_CONFIG = BOT_CONFIG.schedule
```

---

## Key Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Survey Title** | Hardcoded in code | In `bot_config.json` |
| **Survey Options** | Hardcoded in code | In `bot_config.json` |
| **Schedule** | In `schedule_config.json` | In `bot_config.json` |
| **Config Files** | 2 files needed | 1 file needed |
| **Update Survey** | Edit code + redeploy | Edit JSON + restart |
| **Validation** | Basic | Comprehensive |
| **Error Messages** | Generic | Specific & helpful |

---

## Migration Checklist

- [ ] Create `bot_config.json` with survey + schedule sections
- [ ] Update bot script to use `BOT_CONFIG_PATH`
- [ ] Replace `load_schedule_config()` with `load_bot_config()`
- [ ] Remove hardcoded `POLL_QUESTION` and `POLL_OPTIONS`
- [ ] Update `publish_poll()` to use `SURVEY_CONFIG.title` and `SURVEY_CONFIG.options`
- [ ] Test configuration loading
- [ ] Verify poll sends with correct title/options
- [ ] Remove old `schedule_config.json` (optional, for cleanup)

---

## Quick Test

After migration, verify everything works:

```bash
# 1. Check config loads without errors
python bot_refactored.py

# 2. Look for these log messages:
# "Starting bot with configuration from bot_config.json:"
# "  Schedule: start_day=Tuesday 12:00..."
# "  Survey: title='...', options=[...]"

# 3. Send /start command to bot
# Should show survey title and options in response
```
