# HGE Notifier

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

Run the web dashboard:

```pwsh
hge-notifier --web
# then open http://localhost:5000
```

## Configuration

Create a `.env` in the project root (or set environment variables). Example:

```env
# IMPORTANT: Turn off mock mode to connect to real EDDN
EDDN_MOCK_MODE=false

# Set your Elite Dangerous journal directory
# See "Finding Your Journal Folder" below for how to locate this
JOURNAL_PATH=C:\Users\sique\Saved Games\Frontier Developments\Elite Dangerous

# Other optional settings
REFRESH_INTERVAL=10
LOG_LEVEL=INFO
NOTIFICATIONS_ENABLED=false
```

### Finding Your Journal Folder

Your Elite Dangerous journal files are generated in real-time as you play. Each line in these files is a JSON object representing a gameplay event.

**Windows (most common):**
```
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

See `src/config/settings.py` for all available settings and defaults.

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

If you'd like to help improve tests or refactor code, start by reading `DEVELOPMENT_NOTES.md` for targeted areas that would benefit from additional tests.

## Contributing

Contributions are welcome. Please open an issue first if you plan larger changes. Keep changes small and focused; include tests for new behavior.

Follow the project style: black formatting and type hints where practical.

## License

MIT — see the `LICENSE` file for details.

## Contact

Author: CMDR Barateza <contact@example.com>