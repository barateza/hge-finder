# HGE Notifier

<!-- COVERAGE_BADGE_START -->
[![Coverage Status](https://img.shields.io/badge/coverage-81%25-brightgreen?logo=python&logoColor=white)](https://github.com/barateza/eddn-hge)
<!-- COVERAGE_BADGE_END -->
[![Tests](https://img.shields.io/badge/tests-1053%2F1053%20passing-success?logo=pytest)](https://github.com/barateza/eddn-hge)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

_Elite Dangerous is a space simulation game. High Grade Emissions (HGE) are rare signal sources that drop valuable engineering materials. This tool helps you find them in real time._

---

Monitor Elite Dangerous EDDN for High Grade Emission (HGE) signals and see how far they are from your current Commander location.

This repository provides a small Python tool with a CLI and optional web dashboard that:

- listens to the EDDN stream for HGE events
- tracks your local Elite Dangerous journal to determine your latest system
- resolves system coordinates (with a local cache) and computes distances in light-years

For development history and detailed coverage/phase reports see `DEVELOPMENT_NOTES.md`.

## Quick start

Prerequisites: Python 3.9+ and an internet connection (for EDSM lookups and EDDN).

Install in editable mode with dev tools:

```pwsh
git clone https://github.com/barateza/eddn-hge.git
cd eddn-hge
pip install -e ".[dev]"
```

Run the CLI (defaults to a terminal UI):

```pwsh
hge-notifier
```

Run the CLI with real EDDN data:

```pwsh
hge-notifier --real-eddn
```

Run the web dashboard:

```pwsh
hge-notifier --web
# then open http://localhost:5000
```

Run the web dashboard with real EDDN data:

```pwsh
hge-notifier --web --real-eddn
```

See `REAL_EDDN_USAGE.md` for more CLI options and VS Code debug configurations.

## Configuration

Create a `.env` in the project root (or set environment variables). Example:

```env
# IMPORTANT: Turn off mock mode to connect to real EDDN
EDDN_MOCK_MODE=false

# Set your Elite Dangerous journal directory
# See "Finding Your Journal Folder" below for how to locate this
JOURNAL_PATH=C:\Users\sique\Saved Games\Frontier Developments\Elite Dangerous

# Discord notifications (optional)
NOTIFICATIONS_ENABLED=true
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN
ALERT_MAX_DISTANCE=50.0
ALERT_MAX_AGE=24.0

# Other optional settings
REFRESH_INTERVAL=10
LOG_LEVEL=INFO
```

### Finding Your Journal Folder

Your Elite Dangerous journal files are generated in real-time as you play. Each line in these files is a JSON object representing a gameplay event.

**Windows (most common):**

```text
C:\Users\<YourUsername>\Saved Games\Frontier Developments\Elite Dangerous
```

**How to find your username's actual path:**

1. Open EDDiscovery or another third-party tool
2. Check its settings for the journal folder location
3. Or manually navigate: Press `Win+R`, type `%APPDATA%` and work back to find the path

**Files to look for:**

- `Journal.*.log` — These are the journal files the app reads
- They contain events like: `Location`, `FSDJump`, `SupercruiseExit` (location updates)

### ⚠️ Important: Mock Mode is ON by Default

By default, the app runs with `EDDN_MOCK_MODE=true`, which means:

- ❌ It will NOT connect to the real EDDN network
- ❌ It will NOT read your journal file (uses mock location: "Sol")
- ✅ But you can still test the UI

**To use the app for real:**

1. Set `EDDN_MOCK_MODE=false` in `.env`
2. Set `JOURNAL_PATH` to your actual Elite Dangerous journal directory
3. Restart the app

### All Configuration Options

| Setting | Default | Purpose |
|---------|---------|---------|
| `EDDN_MOCK_MODE` | `true` | Set to `false` to use real EDDN |
| `JOURNAL_PATH` | None | Your Elite Dangerous journal directory |
| `NOTIFICATIONS_ENABLED` | `false` | Set to `true` to enable Discord alerts |
| `DISCORD_WEBHOOK_URL` | None | Your Discord webhook URL |
| `ALERT_MAX_DISTANCE` | `50.0` | Alert if HGE is within this many light-years |
| `ALERT_MAX_AGE` | `24.0` | Alert if HGE signal is less than this many hours old |
| `NOTIFICATION_COOLDOWN_SECONDS` | `60` | Minimum seconds between consecutive alerts |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` |
| `LOG_FILE` | None | Optional: write logs to a file |

See `src/config/settings.py` for all available settings and defaults.

## Background Monitoring & Notifications

### Quick Setup: Discord Notifications

1. **Create a Discord Webhook:**
   - Open your Discord server
   - Go to Server Settings → Integrations → Webhooks
   - Click "New Webhook" and name it "HGE Notifier"
   - Choose your notification channel and copy the webhook URL

2. **Add to `.env`:**

   ```env
   NOTIFICATIONS_ENABLED=true
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN
   ```

3. **Run the app:**

   ```pwsh
   D:/repos/eddn-hge/.venv/Scripts/python.exe -m src --real-eddn
   ```

Now whenever an HGE signal is detected within your configured distance, you'll get a Discord message! 🎯

### Running Without Browser

You don't need the web interface open. Choose any method:

#### Option 1: Terminal Window (Simplest)

```pwsh
D:/repos/eddn-hge/.venv/Scripts/python.exe -m src --real-eddn
```

Minimizable; output shows all signals in real-time.

#### Option 2: Windows Scheduled Task (Always-On)

- Create a scheduled task to run the app at login
- App runs in background automatically
- Restarts if it crashes
- See `REAL_EDDN_USAGE.md` for detailed instructions

#### Option 3: With Logging

```pwsh
D:/repos/eddn-hge/.venv/Scripts/python.exe -m src --real-eddn --log-file hge_notifier.log --log-level DEBUG
```

### Notification Filtering

Control which signals trigger notifications:

```env
# Only alert on close, fresh signals
ALERT_MAX_DISTANCE=20.0      # Within 20 ly
ALERT_MAX_AGE=6.0             # Less than 6 hours old
NOTIFICATION_COOLDOWN_SECONDS=600  # Wait 10 min between alerts
```

### Troubleshooting

**No signals appearing?**

- Verify `EDDN_MOCK_MODE=false` in `.env`
- Check internet connection (EDDN requires it)
- Wait longer — EDDN signals can be infrequent
- View logs for errors: `Get-Content hge_notifier.log -Wait`

**Discord notifications not working?**

- Verify webhook URL is correct (copy from Discord again)
- Check channel permissions allow bot posting
- Test manually:

  ```powershell
  $url = "YOUR_WEBHOOK_URL"
  $payload = @{content="Test"} | ConvertTo-Json
  Invoke-WebRequest -Uri $url -Method POST -Body $payload -ContentType "application/json"
  ```

**Location shows N/A?**

- Ensure `JOURNAL_PATH` is correct in `.env`
- Verify journal directory exists: `Test-Path "YOUR_JOURNAL_PATH"`
- Play Elite Dangerous to generate journal entries
- Check logs for coordinate lookup errors

## Project layout

Key folders:

- `src/eddn/` — EDDN ingestion
- `src/journal/` — journal parsing and monitoring
- `src/distance/` — coordinate cache and distance calculations
- `src/web/` — optional Flask dashboard and WebSocket support
- `tests/` — unit and integration tests

## Development

Run the test suite and check coverage:

```pwsh
pytest
```

Formatting and linting:

```pwsh
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Contributing

Contributions are welcome. Please open an issue first if you plan larger changes. Keep changes small and focused; include tests for new behavior.

Follow the project style: black formatting and type hints where practical.

## License

MIT — see the `LICENSE` file for details.

## Contact

Author: CMDR Barateza <advisory@barateza.org>
