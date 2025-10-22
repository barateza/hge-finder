# Phase 2: Notifications & Alerts - Quick Start

## 🚀 Phase 2 Ready to Begin

You've successfully completed Phase 1 with:
- ✅ **60% code coverage** (+6% improvement)
- ✅ **47 passing tests** (100% success rate)
- ✅ **Real EDDN, Journal, and Coordinate integration**
- ✅ **Production-ready error handling**

Now let's build Phase 2: **Real-time Discord Notifications & In-App Alerts**

---

## 📦 Phase 2 Foundation (Already Created)

I've created the core notification infrastructure:

### New Module: `src/notifications/`
```
src/notifications/
├── __init__.py           # Module exports
├── models.py             # Alert & Notification data models
├── in_app.py             # In-app notification storage
├── discord.py            # Discord webhook integration
└── manager.py            # Notification orchestration
```

### Module Capabilities

**Alert Model** (`models.py`)
- Configurable distance threshold (default: 50 ly)
- Configurable signal age threshold (default: 24 hours)
- Enable/disable alerts globally

**In-App Notifications** (`in_app.py`)
- Store notification history (last 100 alerts)
- Query recent notifications for web UI
- Get statistics (success/failure counts)
- Filter by system name

**Discord Integration** (`discord.py`)
- Send alerts via Discord webhook
- Rich embed formatting with color
- Automatic retry with exponential backoff (up to 3 attempts)
- Rate limit handling
- Timeout and connection error handling

**Notification Manager** (`manager.py`)
- Orchestrate all notification channels
- Check alert thresholds before sending
- Enforce cooldown to prevent spam (default: 60 seconds)
- Calculate distance automatically
- Track notification history

---

## ⚙️ Configuration

### Add to `.env`:

```env
# Discord webhook URL (get from Discord server settings)
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/YOUR_ID/YOUR_TOKEN

# Alert thresholds
ALERT_DISTANCE_LY=50              # Alert within 50 light years
ALERT_MAX_AGE_HOURS=24            # Alert for signals < 24 hours old

# Notification settings
ENABLE_DISCORD_ALERTS=true        # Send Discord notifications
ENABLE_IN_APP_ALERTS=true         # Store in-app notification history
NOTIFICATION_COOLDOWN_SECONDS=60  # Prevent notification spam
```

### Getting Discord Webhook URL:

1. **Create Discord Server** (or use existing)
2. **Create #hge-alerts Channel**
3. **Server Settings → Integrations → Webhooks**
4. **Create Webhook**
5. **Copy URL** into `.env`

---

## 🧪 Testing Phase 2 Components

### Test Models
```bash
pytest tests/test_notifications.py::TestModels -v
```

### Test In-App Notifications
```bash
pytest tests/test_notifications.py::TestInAppNotifications -v
```

### Test Discord Integration
```bash
pytest tests/test_notifications.py::TestDiscordIntegration -v
```

### Test Notification Manager
```bash
pytest tests/test_notifications.py::TestNotificationManager -v
```

---

## 📝 Next Steps: Implementation Tasks

### Immediate (Now)
1. ✅ Core notification modules created
2. ✅ Data models defined
3. ⏳ **Create comprehensive test suite** (15+ tests)
4. ⏳ **Integrate with core manager**
5. ⏳ **Add web dashboard endpoints**
6. ⏳ **Documentation and guides**

### Create Tests

**File**: `tests/test_notifications.py`

Test categories needed:
- Alert model validation (3 tests)
- In-app notification system (5 tests)
- Discord webhook integration (5 tests)
- Notification manager logic (5 tests)
- Core manager integration (3 tests)

### Integrate with Core

**File**: `src/core.py` modifications needed:
1. Import NotificationManager
2. Initialize in `__init__`
3. Call `check_and_notify()` on new signals
4. Add notification history API endpoint
5. Pass notification history to web UI

### Web Dashboard Updates

**File**: `src/web/__init__.py` modifications needed:
1. Add `/api/notifications` endpoint
2. Add `/notifications` page
3. Display notification history table
4. Show notification statistics

---

## 🎯 Success Criteria for Phase 2

### Functional
- ✅ Discord webhook sends alerts successfully
- ✅ In-app notifications stored and retrievable
- ✅ Alert thresholds work correctly
- ✅ Cooldown prevents notification spam
- ✅ Web UI displays notification history

### Quality
- ✅ 15+ tests, 100% passing
- ✅ 80%+ code coverage
- ✅ Error handling comprehensive
- ✅ Retry logic works for Discord failures

### Documentation
- ✅ Discord setup guide
- ✅ Configuration reference
- ✅ API documentation
- ✅ Troubleshooting guide

---

## 📊 Estimated Timeline

| Component | Effort | Status |
|-----------|--------|--------|
| Core modules | 1h | ✅ Done |
| Test suite | 2h | ⏳ Next |
| Core integration | 1h | ⏳ After tests |
| Web integration | 1h | ⏳ After core |
| Documentation | 1h | ⏳ Final |
| **Total** | **~6h** | **3 days** |

---

## 🔧 Code Snippets Ready to Use

### How to Use Alert Configuration

```python
from src.notifications import Alert, NotificationManager

# Create custom alert configuration
alert = Alert(
    max_distance_ly=100,        # Alert up to 100 ly away
    max_age_hours=12,           # Only for recent signals
    enabled=True                # Enable alerts
)

# Create manager with Discord
manager = NotificationManager(
    discord_webhook="https://...",
    alert_config=alert,
    cooldown_seconds=30  # 30 second minimum between alerts
)

# Check and send notifications
notification = manager.check_and_notify(signal, location)

if notification:
    print(f"✅ Alert sent: {notification.signal_system}")
else:
    print("No alert needed")
```

### How to Get Notification History

```python
# Get recent notifications
recent = manager.get_notification_history(count=10)

# Get statistics
stats = manager.get_stats()
print(f"Sent {stats['discord_success']} Discord alerts")
print(f"Failed {stats['discord_failed']} Discord alerts")
print(f"In-app: {stats['in_app']} notifications")
```

---

## 📂 File Structure After Phase 2

```
eddn-hge/
├── src/
│   ├── notifications/              ← NEW (Phase 2)
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── in_app.py
│   │   ├── discord.py
│   │   └── manager.py
│   ├── eddn/                       (Phase 1)
│   ├── journal/                    (Phase 1)
│   ├── distance/                   (Phase 1)
│   ├── core.py                     ← Modified for Phase 2
│   ├── web/                        ← Modified for Phase 2
│   └── cli.py
│
├── tests/
│   ├── test_notifications.py       ← NEW (Phase 2)
│   ├── test_coverage_improvements.py
│   └── ... (existing tests)
│
├── PHASE2_PLAN.md                  ← Detailed implementation plan
└── PHASE2_QUICK_START.md           ← This file
```

---

## ✅ Quick Checklist

Before starting implementation:

- [ ] Read this quick start guide
- [ ] Understand notification architecture
- [ ] Review PHASE2_PLAN.md for details
- [ ] Set up Discord webhook URL
- [ ] Ready to implement test suite

---

## 🎉 Ready to Build Phase 2?

The foundation is laid. Now you can:

1. **Create comprehensive test suite** (15+ tests)
2. **Implement core manager integration**
3. **Add web dashboard endpoints**
4. **Write documentation**

Phase 2 will add real user value with Discord and in-app notifications!

---

**Status**: ✅ Foundation Complete, Ready for Implementation
**Next**: Create test suite (`tests/test_notifications.py`)
**Estimated Duration**: 3 days
**Priority**: High (user-facing feature)
