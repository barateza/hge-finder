# HGE Notifier - Elite Dangerous High Grade Emission Monitor

A Python application that monitors the Elite Dangerous Data Network (EDDN) for High Grade Emission (HGE) signals and tracks their distance from your current location.

## Features

### ✅ Phase 1: Real Data Integration Complete

- **Real-time EDDN Monitoring**: Live ZMQ connection to EDDN stream for HGE signals
- **Live Journal Tracking**: Watchdog file monitoring for real-time location updates
- **System Coordinates**: SQLite cache with automatic EDSM API lookups
- **Thread-Safe Operations**: Multi-threaded EDDN monitor and journal watcher
- **Exponential Backoff**: Automatic reconnection with intelligent retry logic
- **CLI Interface**: Command-line interface with real-time updates
- **Web Dashboard**: Flask-based web interface for monitoring
- **Modular Design**: Clean separation of concerns for easy extension

### Core Capabilities
- EDDN ZMQ subscription (tcp://eddn.edcd.io:9500)
- Journal directory monitoring with Watchdog
- System coordinate caching (30-day expiry)
- Graceful error handling and fallbacks
- 31 comprehensive unit tests (100% pass rate)

## Requirements

- Python 3.9 or higher
- Elite Dangerous journal files access
- Internet connection for EDDN data

## Installation

```bash
# Clone the repository
git clone https://github.com/barateza/eddn-hge.git
cd eddn-hge

# Install in development mode
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file in the project root:

```env
# Enable real EDDN and journal
EDDN_MOCK_MODE=false
JOURNAL_PATH=C:\Users\YourUsername\Saved Games\Frontier Developments\Elite Dangerous

# Optional settings
REFRESH_INTERVAL=10
LOG_LEVEL=INFO
EDSM_API_TIMEOUT=5
```

**Note**: See [PHASE1_GUIDE.md](PHASE1_GUIDE.md) for detailed configuration instructions.

## Usage

### Command Line Interface

```bash
hge-notifier
```

### Web Interface

```bash
hge-notifier --web
```

Then navigate to `http://localhost:5000`

## Project Structure

```
src/
├── eddn/          # EDDN data ingestion
├── journal/       # Journal file parsing
├── distance/      # Distance calculations
├── web/           # Flask web interface
├── config/        # Configuration management
└── cli/           # Command-line interface

tests/             # Unit tests
```

## Development

```bash
# Run tests
pytest

# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Architecture

The system uses a modular, thread-safe architecture with real data integration:

```
┌─────────────────────────────────────────────────┐
│        HGE Notifier - Real Data Pipeline        │
└─────────────────────────────────────────────────┘
         │
    ┌────┴────┬──────────────┬──────────────┐
    │          │              │              │
    ▼          ▼              ▼              ▼
┌────────────┐ ┌──────────────┐ ┌───────────────┐
│   EDDN     │ │   Journal    │ │ Coordinates   │
│   ZMQ      │ │   Watchdog   │ │   Database    │
├────────────┤ ├──────────────┤ ├───────────────┤
│ • Real-time│ │ • Live watch │ │ • SQLite      │
│ • Threading│ │ • Event-based│ │ • EDSM API    │
│ • Backoff  │ │ • Callbacks  │ │ • 30d cache   │
└────────────┘ └──────────────┘ └───────────────┘
    │              │              │
    └──────────────┴──────────────┘
              │
              ▼
        ┌──────────────┐
        │ Core Manager │
        │ • Enrichment │
        │ • Status API │
        └──────────────┘
         │             │
         ▼             ▼
      CLI           Web UI
```

### Components

1. **EDDN Module** (`src/eddn/`): ZMQ subscription with exponential backoff reconnection
2. **Journal Module** (`src/journal/`): Watchdog file monitoring for real-time location tracking
3. **Distance Module** (`src/distance/`): SQLite coordinate cache with EDSM API integration
4. **Core Manager** (`src/core.py`): Orchestrates all components and enriches data
5. **CLI/Web** (`src/cli.py`, `src/web/`): User interfaces

## Quality & Testing

- **Code Coverage**: 81% (187 missing lines out of 991 statements)
- **Test Suite**: 241 tests (100% passing, 0 regressions)
- **Perfect Modules**: 7 modules at 100% coverage
- **Excellent Modules**: 8 modules at 90%+
- **Perfect Status**: 7 modules completely covered

### Coverage by Module
| Module | Coverage | Status |
|--------|----------|--------|
| in_app.py | 100% | ✅ Perfect |
| settings.py | 100% | ✅ Perfect |
| manager.py | 100% | ✅ Perfect |
| models.py | 100% | ✅ Perfect |
| cli.py | 100% | ✅ Perfect |
| __main__.py | 100% | ✅ Perfect |
| core.py | 65% | 🔄 In Progress |
| eddn/__init__.py | 68% | 🔄 In Progress |
| journal/__init__.py | 85% | ✅ Good |

## Phase Status

### ✅ Phase 1: Real Data Integration (COMPLETE)

All core real-time features implemented and tested:
- EDDN ZMQ connection with reconnection logic ✅
- Watchdog journal file monitoring ✅
- EDSM API coordinate lookups with SQLite caching ✅
- Comprehensive error handling and logging ✅
- **80 tests** (79% coverage)

### ✅ Phase 2: Notifications & Alerts (COMPLETE)

Notification system with Discord and in-app notifications:
- Discord webhook notifications ✅
- In-app notification history ✅
- Notification styling and formatting ✅
- 100 tests total (+36 from Phase 2)
- **80% coverage** achieved

### ✅ Phase 3: Edge Cases & Advanced Testing (IN PROGRESS)

**Phase 3.1 - EASY** (Complete):
- Distance calculation edge cases ✅
- In-app notification edge cases ✅
- Coordinates caching edge cases ✅
- **+38 tests**, 80% coverage maintained

**Phase 3.2 - MEDIUM** (Complete):
- Journal file I/O edge cases ✅
- Coordinate extraction comprehensive tests ✅
- Journal module improved 78% → 85% ✅
- **+23 tests**, 81% coverage achieved

**Phase 3.3 - HARD** (Next: 7-9 hours):
- EDDN network error testing (~18 tests)
- Core orchestration edge cases (~15 tests)
- Target: 85%+ coverage

### 🔜 Future Phases

- **Phase 3.4**: WebSocket real-time updates
- **Phase 3.5**: Advanced dashboard features
- **Phase 4**: Route planning and filtering
- **Phase 5**: Distribution and auto-updates

## Contributing

Contributions are welcome! Please ensure code follows PEP-8 and includes type hints.

## License

MIT License - See LICENSE file for details
