# Refactoring Summary: schedule_config.json → bot_config.json

## Overview

The bot has been refactored to consolidate all configuration into a single `bot_config.json` file, moving survey content from hardcoded values in the source code to the configuration file.

---

## Changes Made

### 1. Configuration File Changes

**Old:** `schedule_config.json` (scheduling only)
**New:** `bot_config.json` (survey content + scheduling)

### 2. Code Changes

- ✅ Renamed `SCHEDULE_CONFIG_PATH` → `BOT_CONFIG_PATH`
- ✅ Removed hardcoded `POLL_QUESTION` and `POLL_OPTIONS` constants
- ✅ Added `SurveyConfig` dataclass
- ✅ Added `BotConfig` dataclass (combines survey + schedule)
- ✅ Updated `load_schedule_config()` → `load_bot_config()`
- ✅ Enhanced error handling with detailed validation
- ✅ Updated all references to use `SURVEY_CONFIG` and `SCHEDULE_CONFIG` from `BOT_CONFIG`

---

## New Configuration File Structure

### `bot_config.json`

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

## Validation Rules

The code now validates:

### Survey Section
- ✅ `title` must be a non-empty string
- ✅ `options` must be a list
- ✅ Must have 2-10 options
- ✅ Each option must be a non-empty string

### Schedule Section
- ✅ `start_day` and `stop_day` must be valid day names
- ✅ `start_time` and `stop_time` must be in "HH:MM" format (24-hour)
- ✅ Time values must be valid (hour: 0-23, minute: 0-59)
- ✅ `timezone` must be a valid IANA timezone identifier

---

## Error Handling

The refactored code includes comprehensive error handling:

1. **File Not Found**: Clear error message indicating which file is missing
2. **Invalid JSON**: Catches JSON parsing errors with context
3. **Missing Sections**: Validates required sections exist
4. **Invalid Values**: Validates data types and value ranges
5. **Configuration Errors**: Provides specific error messages pointing to the problem

### Example Error Messages

```
Error: bot_config.json: 'survey.title' must be a non-empty string
Error: bot_config.json: 'survey.options' must contain at least 2 options
Error: bot_config.json: Invalid schedule format - Invalid day name 'Tuesdy'. Must be one of: Monday, Tuesday, ...
Error: bot_config.json: Invalid timezone 'Invalid/TZ': Invalid timezone
```

---

## Migration Steps

### Step 1: Create `bot_config.json`

Copy your existing `schedule_config.json` and add the survey section:

```bash
# If you have schedule_config.json, you can manually merge it
# Or use the provided bot_config.json template
```

### Step 2: Update Your Bot Script

Replace your old bot script with `bot_refactored.py`, or manually update:

1. Change `SCHEDULE_CONFIG_PATH` to `BOT_CONFIG_PATH`
2. Replace `load_schedule_config()` with `load_bot_config()`
3. Remove hardcoded `POLL_QUESTION` and `POLL_OPTIONS`
4. Update references to use `SURVEY_CONFIG.title` and `SURVEY_CONFIG.options`

### Step 3: Test Configuration

```bash
# Test that the config loads correctly
python bot_refactored.py

# Check logs for configuration summary
```

---

## Benefits

1. **Single Configuration File**: All settings in one place
2. **No Code Changes for Survey Updates**: Change title/options without touching code
3. **Better Validation**: Comprehensive error checking
4. **Clearer Structure**: Separated survey content from scheduling
5. **Easier Maintenance**: Update survey without redeploying code

---

## Backward Compatibility

⚠️ **Breaking Change**: The old `schedule_config.json` format is no longer supported. You must migrate to `bot_config.json`.

---

## Example Usage

### Changing Survey Title

Edit `bot_config.json`:
```json
{
  "survey": {
    "title": "New survey question here",
    ...
  }
}
```

Restart bot - no code changes needed!

### Adding/Removing Options

Edit `bot_config.json`:
```json
{
  "survey": {
    "options": [
      "Option 1",
      "Option 2",
      "New Option 3"
    ]
  }
}
```

Restart bot - changes take effect immediately!

---

## Testing

To verify the configuration loads correctly:

```python
# The bot will log configuration on startup:
# Starting bot with configuration from bot_config.json:
#   Schedule: start_day=Tuesday 12:00, stop_day=Thursday 20:00, tz=Europe/Berlin
#   Survey: title='...', options=[...]
```

If there are errors, they will be displayed clearly with specific guidance on what needs to be fixed.
