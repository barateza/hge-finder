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
EDDN_MOCK_MODE=false
JOURNAL_PATH=C:\Users\<You>\Saved Games\Frontier Developments\Elite Dangerous
REFRESH_INTERVAL=10
LOG_LEVEL=INFO
```

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