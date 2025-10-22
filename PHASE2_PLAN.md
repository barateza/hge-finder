# Phase 2: Notifications & Alerts - Implementation Plan

## 🎯 Phase 2 Objective

Implement real-time notification system for HGE alerts via Discord and in-app notifications, enabling users to be instantly notified of new High Grade Emission signals with configurable thresholds.

---

## 📋 What Will Be Delivered

### Core Features
- ✅ Discord webhook integration for real-time HGE alerts
- ✅ In-app notification system with history tracking
- ✅ Configurable alert thresholds (distance, signal age)
- ✅ Notification preferences and management
- ✅ Error handling and retry logic
- ✅ Comprehensive test suite (15+ tests)
- ✅ Professional documentation

### Non-Goals (Phase 2)
- ❌ Email notifications (removed per requirements)
- ❌ Push notifications (phone/mobile)
- ❌ WebSocket real-time web updates (Phase 3)
- ❌ Advanced UI changes (Phase 3)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         HGE Notifier - Phase 2                  │
│     Notifications & Alerts System               │
└─────────────────────────────────────────────────┘
         │
    ┌────┴────────────────────┐
    │                         │
    ▼                         ▼
┌──────────────┐      ┌──────────────────┐
│   Discord    │      │   In-App         │
│ Notifications│      │ Notifications    │
├──────────────┤      ├──────────────────┤
│ • Webhooks   │      │ • History queue  │
│ • Embeds     │      │ • Status API     │
│ • Retry      │      │ • Preferences    │
│ • Rate limit │      │ • Web display    │
└──────────────┘      └──────────────────┘
    │                         │
    └────────────┬────────────┘
                 │
                 ▼
         ┌──────────────┐
         │ Notification │
         │  Manager     │
         ├──────────────┤
         │ • Triggers   │
         │ • Filtering  │
         │ • Throttling │
         │ • Callbacks  │
         └──────────────┘
                 │
                 ▼
         ┌──────────────┐
         │ Core Manager │
         │ Integration  │
         └──────────────┘
```

---

## 📦 Module Structure

### New Directory: `src/notifications/`

```
src/notifications/
├── __init__.py                 # Module initialization
├── manager.py                  # Notification manager (orchestration)
├── discord.py                  # Discord webhook integration
├── in_app.py                   # In-app notification storage
└── models.py                   # Data models (Notification, Alert)
```

### Configuration: `.env`

```env
# Phase 2: Notification Configuration

# Discord Webhook URL for HGE alerts
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN

# Alert Thresholds
ALERT_DISTANCE_LY=50           # Alert when HGE is within N light years
ALERT_MAX_AGE_HOURS=24         # Only alert for signals less than N hours old

# Notification Settings
ENABLE_DISCORD_ALERTS=true      # Enable Discord notifications
ENABLE_IN_APP_ALERTS=true       # Enable in-app notifications
NOTIFICATION_COOLDOWN_SECONDS=60 # Prevent spam (min seconds between alerts)
NOTIFICATION_HISTORY_SIZE=100   # Keep last N notifications in memory
```

---

## 🔧 Implementation Tasks

### Sprint 1: Core Infrastructure (Day 1-2)

#### Task 1.1: Create Notification Models
**File**: `src/notifications/models.py`

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Alert:
    """Represents an alert threshold configuration."""
    max_distance_ly: float = 50
    max_age_hours: int = 24
    enabled: bool = True

@dataclass
class Notification:
    """Represents a sent notification."""
    signal_system: str
    distance_ly: float
    timestamp: datetime
    channel: str  # 'discord', 'in_app'
    success: bool
    error: Optional[str] = None
```

**Tests**:
- [ ] test_alert_model_creation
- [ ] test_notification_model_creation
- [ ] test_alert_validation

#### Task 1.2: Create In-App Notification System
**File**: `src/notifications/in_app.py`

```python
class InAppNotificationSystem:
    """Store and manage in-app notifications."""
    
    def __init__(self, max_history: int = 100):
        self.history = []  # List of Notification objects
        self.max_history = max_history
    
    def add_notification(self, notification: Notification) -> None:
        """Add notification to history."""
        self.history.append(notification)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_recent(self, count: int = 10) -> List[Notification]:
        """Get recent notifications."""
        return self.history[-count:]
    
    def clear_history(self) -> None:
        """Clear notification history."""
        self.history.clear()
    
    def get_stats(self) -> dict:
        """Get notification statistics."""
        return {
            'total': len(self.history),
            'discord_success': sum(1 for n in self.history if n.channel == 'discord' and n.success),
            'in_app_count': sum(1 for n in self.history if n.channel == 'in_app'),
        }
```

**Tests**:
- [ ] test_add_notification
- [ ] test_get_recent_notifications
- [ ] test_max_history_limit
- [ ] test_clear_history
- [ ] test_notification_stats

#### Task 1.3: Create Discord Integration
**File**: `src/notifications/discord.py`

```python
class DiscordNotificationService:
    """Send alerts to Discord via webhook."""
    
    def __init__(self, webhook_url: str, timeout: int = 5):
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.retry_count = 3
    
    def send_alert(self, 
                   system_name: str, 
                   distance_ly: float,
                   coordinates: Tuple[float, float, float],
                   signal_age_hours: float) -> Notification:
        """Send HGE alert to Discord."""
        
    def _build_embed(self, system_name: str, ...) -> dict:
        """Build Discord embed message."""
        
    def _send_with_retry(self, payload: dict) -> bool:
        """Send to Discord with exponential backoff."""
```

**Message Format**:
```
🎯 NEW HGE SIGNAL DETECTED

System: Shinrarta Dezhra
Distance: 35.28 ly
Coordinates: (55.72, -49.50, 17.40)
Signal Age: 2m ago
Detection Time: 2025-10-22 10:30:45

[Click to go to system]
```

**Tests**:
- [ ] test_build_embed_message
- [ ] test_send_alert_success
- [ ] test_send_alert_webhook_timeout
- [ ] test_send_alert_invalid_webhook
- [ ] test_retry_logic

### Sprint 2: Manager & Integration (Day 2-3)

#### Task 2.1: Create Notification Manager
**File**: `src/notifications/manager.py`

```python
class NotificationManager:
    """Orchestrate notification delivery across channels."""
    
    def __init__(self, 
                 discord_webhook: Optional[str] = None,
                 alert_config: Optional[Alert] = None):
        self.discord = DiscordNotificationService(discord_webhook) if discord_webhook else None
        self.in_app = InAppNotificationSystem()
        self.alerts = alert_config or Alert()
        self.last_notification_time = None
        self.cooldown_seconds = 60
    
    def check_and_notify(self, signal: HGESignal, location: CommanderLocation) -> None:
        """Check if signal meets alert criteria and send notifications."""
        
        # Calculate distance
        distance = self._calculate_distance(signal, location)
        
        # Check thresholds
        if not self._meets_threshold(signal, distance):
            return
        
        # Check cooldown
        if not self._check_cooldown():
            return
        
        # Send notifications
        self._send_notifications(signal, distance, location)
    
    def _meets_threshold(self, signal: HGESignal, distance: float) -> bool:
        """Check if signal meets alert thresholds."""
        if not self.alerts.enabled:
            return False
        
        if distance > self.alerts.max_distance_ly:
            return False
        
        age_hours = signal.age_seconds() / 3600
        if age_hours > self.alerts.max_age_hours:
            return False
        
        return True
    
    def _send_notifications(self, signal, distance, location):
        """Send to all configured notification channels."""
```

**Tests**:
- [ ] test_manager_initialization
- [ ] test_check_threshold_distance
- [ ] test_check_threshold_age
- [ ] test_cooldown_enforcement
- [ ] test_send_all_channels

#### Task 2.2: Integrate with Core Manager
**File**: `src/core.py` (modifications)

```python
class HGENotifierManager:
    
    def __init__(self, ...):
        # ... existing code ...
        
        # Initialize notification system
        discord_url = settings.get("DISCORD_WEBHOOK_URL")
        self.notification_manager = NotificationManager(
            discord_webhook=discord_url,
            alert_config=Alert(
                max_distance_ly=settings.get("ALERT_DISTANCE_LY", 50),
                max_age_hours=settings.get("ALERT_MAX_AGE_HOURS", 24),
            )
        )
    
    def _on_new_hge_signal(self, signal: HGESignal) -> None:
        """Enhanced: Check and send notifications."""
        # ... existing code ...
        
        # Check if we should notify
        if self.last_location:
            self.notification_manager.check_and_notify(signal, self.last_location)
    
    def get_notification_history(self) -> List[Notification]:
        """Get recent notifications for API/web display."""
        return self.notification_manager.in_app.get_recent(10)
```

**Tests**:
- [ ] test_notification_on_signal
- [ ] test_notification_with_threshold
- [ ] test_no_notification_outside_range

#### Task 2.3: Add Web Dashboard Integration
**File**: `src/web/__init__.py` (modifications)

```python
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get recent notifications."""
    notifications = manager.get_notification_history()
    return jsonify([
        {
            'system': n.signal_system,
            'distance': n.distance_ly,
            'timestamp': n.timestamp.isoformat(),
            'channel': n.channel,
        }
        for n in notifications
    ])

@app.route('/notifications', methods=['GET'])
def notifications_page():
    """Display notification history on web UI."""
    # Render template with notification table
```

**Tests**:
- [ ] test_notification_api_endpoint
- [ ] test_notification_page_rendering

### Sprint 3: Testing & Documentation (Day 3)

#### Task 3.1: Comprehensive Test Suite

**File**: `tests/test_notifications.py` (NEW)

```python
class TestDiscordIntegration:
    def test_send_alert_success(self)
    def test_send_alert_timeout(self)
    def test_send_alert_invalid_webhook(self)
    def test_retry_logic(self)
    def test_rate_limiting(self)

class TestInAppNotifications:
    def test_add_notification(self)
    def test_history_limit(self)
    def test_get_recent(self)
    def test_stats(self)

class TestNotificationManager:
    def test_threshold_checking(self)
    def test_cooldown(self)
    def test_multi_channel(self)
    def test_error_handling(self)

class TestCoreIntegration:
    def test_notification_on_signal(self)
    def test_notification_with_location(self)
```

**Coverage Target**: 80%+

#### Task 3.2: Documentation

**File**: `PHASE2_GUIDE.md`

Content:
- Discord webhook setup guide
- Configuration reference
- Usage examples
- Troubleshooting
- API reference

---

## 📊 Implementation Timeline

| Day | Task | Deliverable |
|-----|------|-------------|
| Day 1 | Models + In-App System | `in_app.py` + tests |
| Day 1-2 | Discord Integration | `discord.py` + tests |
| Day 2 | Manager + Core Integration | `manager.py` + integration |
| Day 2-3 | Testing & Documentation | Tests + guides |
| Day 3 | Final review & polish | All tests passing |

**Total Effort**: 3 days
**Total Tests**: 15+ new tests
**Total Documentation**: Comprehensive Phase 2 guide

---

## 📝 Configuration Setup

### User Setup Steps

1. **Create Discord Server & Get Webhook**
   ```
   1. Create Discord server or use existing
   2. Create a new channel: #hge-alerts
   3. Server Settings → Integrations → Webhooks
   4. Create Webhook, copy URL
   ```

2. **Configure .env**
   ```env
   DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/YOUR_ID/YOUR_TOKEN
   ALERT_DISTANCE_LY=50
   ALERT_MAX_AGE_HOURS=24
   ENABLE_DISCORD_ALERTS=true
   ENABLE_IN_APP_ALERTS=true
   ```

3. **Test Configuration**
   ```bash
   python -m src --test-notifications
   # Should send test alert to Discord
   ```

---

## 🎯 Success Criteria

### Functional
- ✅ Discord alerts send successfully
- ✅ In-app notifications display in web UI
- ✅ Thresholds work correctly
- ✅ Error handling is robust
- ✅ Cooldown prevents spam

### Quality
- ✅ 15+ tests, 100% passing
- ✅ 80%+ code coverage
- ✅ No critical bugs
- ✅ Error messages are clear

### Documentation
- ✅ Setup guide completed
- ✅ Configuration documented
- ✅ API reference provided
- ✅ Troubleshooting guide included

---

## 🚀 Rollout Plan

### Internal Testing
1. Configure Discord webhook in test server
2. Run full test suite (15+ tests)
3. Manual testing with real signals
4. Verify all alert thresholds work

### Beta Release
1. Document setup in PHASE2_GUIDE.md
2. Push to main branch
3. Create release notes
4. Tag version 0.2.0

### User Release
1. Update README with Phase 2 features
2. Publish setup guide
3. Announce on community channels

---

## 📚 References

- Discord Webhook Documentation: https://discord.com/developers/docs/resources/webhook
- Rate Limiting Best Practices: https://discord.com/developers/docs/resources/webhook#rate-limiting
- Webhook Payload Format: https://discord.com/developers/docs/resources/webhook#webhook-object

---

## ✅ Checklist

### Pre-Implementation
- [ ] Phase 2 plan approved
- [ ] Tasks broken down and prioritized
- [ ] Testing strategy defined
- [ ] Documentation plan created

### During Implementation
- [ ] Code follows PEP-8 standards
- [ ] Type hints added throughout
- [ ] Tests written as features are built
- [ ] Docstrings completed
- [ ] Error handling comprehensive

### Pre-Release
- [ ] All 15+ tests passing
- [ ] Coverage at 80%+
- [ ] Documentation complete
- [ ] Manual testing done
- [ ] Code reviewed

### Post-Release
- [ ] Guide published
- [ ] Version tagged
- [ ] Release notes created
- [ ] Community notified

---

## 🎉 Ready to Start?

This Phase 2 plan delivers:
- ✅ Real-time Discord alerts for HGE
- ✅ In-app notification history
- ✅ Configurable alert thresholds
- ✅ Production-ready error handling
- ✅ Comprehensive testing & documentation

**Next Step**: Begin Sprint 1 - Core Infrastructure

---

**Status**: Ready for Implementation
**Estimated Duration**: 3 days
**Priority**: High (user-facing feature)
**Dependencies**: Phase 1 (complete)
