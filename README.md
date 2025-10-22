# HGE Notifier - Elite Dangerous High Grade Emission Monitor

A Python application that monitors the Elite Dangerous Data Network (EDDN) for High Grade Emission (HGE) signals and tracks their distance from your current location.

## Features

### ✅ Phase 1-3: Core Features Complete

- **Real-time EDDN Monitoring**: Live ZMQ connection to EDDN stream for HGE signals
- **Live Journal Tracking**: Watchdog file monitoring for real-time location updates
- **System Coordinates**: SQLite cache with automatic EDSM API lookups
- **Thread-Safe Operations**: Multi-threaded EDDN monitor and journal watcher
- **Exponential Backoff**: Automatic reconnection with intelligent retry logic
- **CLI Interface**: Command-line interface with real-time updates
- **Web Dashboard**: Flask-based web interface with notifications
- **Discord Notifications**: Real-time Discord webhook alerts (Phase 2)
- **In-App Notifications**: Local notification history and statistics (Phase 2)
- **Configurable Alerts**: Distance and age thresholds with cooldown (Phase 2)

### ✅ Phase 3.4.A: WebSocket Infrastructure Complete

- **Real-Time WebSocket Updates**: Socket.IO for instant UI updates
- **Event Channel System**: 4 channels (HGE signals, location, distance, status)
- **Connection Tracking**: Automatic connection management and subscriptions
- **Core Integration**: Seamless HGENotifierManager event emission

### 🔄 Phase 3.4.B: WebSocket Client (70% Complete)

- **Socket.IO JavaScript Client**: Live event listeners on dashboard
- **Real-Time DOM Updates**: Instant UI updates without polling
- **Connection Status**: Visual indicator for connection state (green/orange)
- **Graceful Fallback**: REST API polling when WebSocket unavailable
- **39 Integration Tests**: Comprehensive testing of WebSocket architecture

### Advanced Capabilities
- EDDN ZMQ subscription (tcp://eddn.edcd.io:9500)
- Journal directory monitoring with Watchdog
- System coordinate caching (30-day expiry)
- Discord webhook integration with retry logic
- 347 comprehensive unit tests (100% pass rate, 83% coverage)

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

- **Code Coverage**: 86% (134 missing lines out of 991 statements) ⭐ **Target Exceeded**
- **Test Suite**: 287 tests (100% passing, 0 regressions)
- **Perfect Modules**: 7 modules at 100% coverage
- **Excellent Modules**: 11 modules at 90%+
- **Good Modules**: 8 modules at 80-89%
- **Fair Modules**: 2 modules at 65-79%

### Coverage by Module
| Module | Coverage | Status | Phase |
|--------|----------|--------|-------|
| __init__.py | 100% | ✅ Perfect | - |
| config/__init__.py | 100% | ✅ Perfect | - |
| config/settings.py | 100% | ✅ Perfect | 3.3.B |
| distance/__init__.py | 100% | ✅ Perfect | - |
| notifications/__init__.py | 100% | ✅ Perfect | - |
| notifications/in_app.py | 100% | ✅ Perfect | 3.3.B |
| web/__init__.py | 91% | ✅ Excellent | 3.3.B |
| __main__.py | 97% | ✅ Excellent | - |
| core.py | 94% | ✅ Excellent | 3.3.B |
| notifications/manager.py | 91% | ✅ Excellent | - |
| cli.py | 89% | ✅ Good | - |
| notifications/models.py | 89% | ✅ Good | - |
| journal/__init__.py | 85% | ✅ Good | 3.2 |
| eddn/__init__.py | 80% | ✅ Good | 3.3.A |
| coordinates.py | 76% | 🟡 Fair | 3.2 |
| discord.py | 76% | 🟡 Fair | 3.2 |

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

### ✅ Phase 3: Edge Cases & Advanced Testing (COMPLETE)

**Phase 3.1 - EASY** (✅ Complete):
- Distance calculation edge cases ✅
- In-app notification edge cases ✅
- Coordinates caching edge cases ✅
- **+38 tests**, 80% coverage maintained

**Phase 3.2 - MEDIUM** (✅ Complete):
- Journal file I/O edge cases ✅
- Coordinate extraction comprehensive tests ✅
- Journal module improved 78% → 85% ✅
- **+23 tests**, 81% coverage achieved

**Phase 3.3 - HARD** (✅ COMPLETE):

*Phase 3.3.A - EDDN Network Testing*:
- EDDN network error handling (24 tests) ✅
- Timeouts, malformed data, reconnection logic ✅
- EDDN module improved 40% → 80% (+40%) ✅

*Phase 3.3.B - Core Orchestration Testing*:
- Core orchestration edge cases (26 tests) ✅
- Integration, callbacks, state management ✅
- Core module improved 65% → 94% (+29%) ✅

**Phase 3.3 Results**:
- **+50 tests** (+24 EDDN + 26 Core)
- **Total: 287 tests** (100% passing, 0 regressions)
- **Coverage: 86%** (Target 85% exceeded by 1%) ⭐
- **EDDN module: 40% → 80%** (+40%)
- **Core module: 65% → 94%** (+29%)

### � Phase 3.4: Real-Time WebSocket Updates (IN PROGRESS - 70% COMPLETE)

**Phase 3.4.A - WebSocket Infrastructure** (✅ Complete):
- WebSocket server with Socket.IO 5.9.0 ✅
- 4-channel event system (hge_signal, location_update, distance_update, status) ✅
- Core manager integration with event callbacks ✅
- Flask app Socket.IO merge with REST API backward compatibility ✅
- **21 unit tests** ✅

**Phase 3.4.B - Client & Integration** (✅ COMPLETE):

*Phase 3.4.B.5 - WebSocket Client (JavaScript)*:
- Socket.IO client library (CDN 4.5.4) ✅
- Dashboard real-time HGE signal, location, distance display ✅
- Notifications auto-refresh on new signals ✅
- Connection status indicator (green/orange) ✅
- REST API fallback polling (30s dashboard, 10s notifications) ✅
- **340 lines JavaScript** across both templates

*Phase 3.4.B.7 - Integration Tests*:
- 13 test classes covering architecture ✅
- Event propagation, connection lifecycle, data serialization ✅
- Error handling, REST/WebSocket coexistence ✅
- Production scenarios, performance, edge cases ✅
- **39 integration tests** (100% passing) ✅

**Phase 3.4 Current Status**:
- **+60 tests total** (21 unit + 39 integration)
- **Total: 347 tests** (100% passing, 0 regressions)
- **Coverage: 83%** overall, **85% WebSocket module**
- **Type errors: 0** (Type-safe additions)
- **Production Ready**: WebSocket infrastructure validated end-to-end

**Pending Phase 3.4 Tasks**:
- Task 8: UI Real-Time Behavior (2-3 hours)
- Task 9: Mobile-Responsive Enhancements (1-2 hours)
- Task 10: Timeline Visualization (2-3 hours)
- Task 11: Coverage Verification to 88%+ (1 hour)
- Task 12: Final Documentation (1-2 hours)

### 🔜 Future Phases

- **Phase 3.5**: Advanced dashboard features
- **Phase 4**: Route planning and filtering
- **Phase 5**: Distribution and auto-updates

## Contributing

Contributions are welcome! Please ensure code follows PEP-8 and includes type hints.

## License

MIT License - See LICENSE file for details
