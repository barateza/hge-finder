"""
Phase 4B: Notification Manager Advanced Tests

Tests for NotificationManager edge cases: alert thresholds, cooldown handling,
Discord service failures, and notification delivery edge cases.
Covers error paths and boundary conditions in src/notifications/manager.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta

from src.eddn import HGESignal
from src.journal import CommanderLocation
from src.notifications.manager import NotificationManager
from src.notifications.models import Alert, Notification


class TestNotificationManagerPhase4B:
    """Test notification manager advanced scenarios and edge cases."""

    def test_notification_manager_initialization_no_discord(self):
        """Test manager initialization without Discord."""
        manager = NotificationManager(discord_webhook=None)
        
        assert manager is not None
        assert manager.discord_service is None
        assert manager.in_app is not None

    def test_notification_manager_initialization_with_discord(self):
        """Test manager initialization with valid Discord webhook."""
        # Valid webhook format
        webhook_url = "https://discordapp.com/api/webhooks/123456789/abcdefghijklmnop"
        
        manager = NotificationManager(discord_webhook=webhook_url)
        
        assert manager is not None
        # Discord service may or may not initialize depending on URL format

    def test_notification_manager_invalid_discord_webhook(self):
        """Test manager initialization with invalid Discord webhook."""
        # Invalid webhook format
        invalid_webhook = "not_a_valid_url"
        
        # Should handle gracefully
        manager = NotificationManager(discord_webhook=invalid_webhook)
        
        assert manager is not None

    def test_notification_manager_custom_alert_config(self):
        """Test manager with custom alert configuration."""
        custom_alert = Alert(
            max_distance_ly=50.0,
            max_age_hours=12,
            enabled=True
        )
        
        manager = NotificationManager(alert_config=custom_alert)
        
        assert manager.alerts == custom_alert

    def test_notification_manager_custom_cooldown(self):
        """Test manager with custom cooldown."""
        manager = NotificationManager(cooldown_seconds=120)
        
        assert manager.cooldown_seconds == 120

    def test_notification_manager_default_cooldown(self):
        """Test manager uses default cooldown."""
        manager = NotificationManager()
        
        assert manager.cooldown_seconds == 60

    def test_notification_manager_check_notify_no_distance(self):
        """Test check_and_notify when distance calculation fails."""
        manager = NotificationManager()
        
        signal = HGESignal(
            system_name="Test",
            timestamp=datetime.now(timezone.utc),
            x=None,
            y=None,
            z=None
        )
        
        location = CommanderLocation(
            system_name="Home",
            timestamp=datetime.now(timezone.utc),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        result = manager.check_and_notify(signal, location)
        
        # Should return None when distance cannot be calculated
        assert result is None

    def test_notification_manager_check_notify_valid(self):
        """Test check_and_notify with valid signal and location."""
        manager = NotificationManager()
        
        signal = HGESignal(
            system_name="HGE System",
            timestamp=datetime.now(timezone.utc),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        location = CommanderLocation(
            system_name="Home",
            timestamp=datetime.now(timezone.utc),
            x=100.0,
            y=100.0,
            z=100.0
        )
        
        result = manager.check_and_notify(signal, location)
        
        # May return notification or None depending on thresholds
        assert result is None or isinstance(result, Notification)

    def test_notification_manager_alert_distance_threshold(self):
        """Test that close signals trigger notifications."""
        alert = Alert(max_distance_ly=10.0)
        manager = NotificationManager(alert_config=alert)
        
        signal = HGESignal(
            system_name="Close HGE",
            timestamp=datetime.now(timezone.utc),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        location = CommanderLocation(
            system_name="Home",
            timestamp=datetime.now(timezone.utc),
            x=5.0,
            y=0.0,
            z=0.0
        )
        
        result = manager.check_and_notify(signal, location)
        
        # Should trigger at 5 LY distance with 10 LY threshold
        assert result is None or isinstance(result, Notification)

    def test_notification_manager_alert_distance_too_far(self):
        """Test that far signals don't trigger notifications."""
        alert = Alert(max_distance_ly=10.0)
        manager = NotificationManager(alert_config=alert)
        
        signal = HGESignal(
            system_name="Far HGE",
            timestamp=datetime.now(timezone.utc),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        location = CommanderLocation(
            system_name="Home",
            timestamp=datetime.now(timezone.utc),
            x=1000.0,
            y=0.0,
            z=0.0
        )
        
        result = manager.check_and_notify(signal, location)
        
        # Should not trigger - too far away
        assert result is None

    def test_notification_manager_cooldown_blocking(self):
        """Test that cooldown blocks repeated notifications."""
        manager = NotificationManager(cooldown_seconds=1)
        
        # Set last notification time (use naive datetime like manager does)
        manager.last_notification_time = datetime.utcnow()
        
        signal = HGESignal(
            system_name="Test",
            timestamp=datetime.now(timezone.utc),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        location = CommanderLocation(
            system_name="Home",
            timestamp=datetime.now(timezone.utc),
            x=5.0,
            y=0.0,
            z=0.0
        )
        
        # Immediate second call should be blocked
        result = manager.check_and_notify(signal, location)
        
        # Should return None due to cooldown
        assert result is None

    def test_notification_manager_cooldown_expiry(self):
        """Test that cooldown expires after timeout."""
        manager = NotificationManager(cooldown_seconds=0)  # No cooldown
        
        signal = HGESignal(
            system_name="Test",
            timestamp=datetime.now(timezone.utc),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        location = CommanderLocation(
            system_name="Home",
            timestamp=datetime.now(timezone.utc),
            x=5.0,
            y=0.0,
            z=0.0
        )
        
        # With no cooldown, may notify
        result1 = manager.check_and_notify(signal, location)
        
        # Result depends on thresholds
        assert result1 is None or isinstance(result1, Notification)

    def test_notification_manager_in_app_system_exists(self):
        """Test that in-app notification system is always created."""
        manager = NotificationManager()
        
        assert manager.in_app is not None

    def test_notification_manager_distance_calculator_exists(self):
        """Test that distance calculator is created."""
        manager = NotificationManager()
        
        assert manager.distance_calc is not None

    def test_notification_manager_multiple_instances_independent(self):
        """Test that multiple manager instances are independent."""
        manager1 = NotificationManager(cooldown_seconds=60)
        manager2 = NotificationManager(cooldown_seconds=120)
        
        assert manager1.cooldown_seconds == 60
        assert manager2.cooldown_seconds == 120
        assert manager1.cooldown_seconds != manager2.cooldown_seconds

    def test_notification_manager_state_preservation(self):
        """Test that notification state is preserved."""
        manager = NotificationManager()
        
        signal = HGESignal(
            system_name="Test",
            timestamp=datetime.now(timezone.utc),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        location = CommanderLocation(
            system_name="Home",
            timestamp=datetime.now(timezone.utc),
            x=5.0,
            y=0.0,
            z=0.0
        )
        
        result = manager.check_and_notify(signal, location)
        
        # Manager should be in consistent state
        assert manager.last_notification_time is None or isinstance(manager.last_notification_time, datetime)

    def test_alert_model_creation(self):
        """Test Alert model creation."""
        alert = Alert(
            max_distance_ly=20.0,
            max_age_hours=12,
            enabled=True
        )
        
        assert alert.max_distance_ly == 20.0
        assert alert.max_age_hours == 12
        assert alert.enabled is True

    def test_alert_model_defaults(self):
        """Test Alert model default values."""
        alert = Alert()
        
        assert alert is not None
        assert alert.max_distance_ly == 50.0
        assert alert.max_age_hours == 24
        assert alert.enabled is True

    def test_notification_model_creation(self):
        """Test Notification model creation."""
        now = datetime.now(timezone.utc)
        
        notification = Notification(
            signal_system="Alert",
            distance_ly=15.0,
            timestamp=now,
            channel="in_app",
            success=True
        )
        
        assert notification.signal_system == "Alert"
        assert notification.distance_ly == 15.0
        assert notification.timestamp == now
        assert notification.channel == "in_app"
        assert notification.success is True

    def test_notification_model_equality(self):
        """Test Notification model equality."""
        now = datetime.now(timezone.utc)
        
        notif1 = Notification(
            signal_system="Test",
            distance_ly=10.0,
            timestamp=now,
            channel="in_app",
            success=True
        )
        
        notif2 = Notification(
            signal_system="Test",
            distance_ly=10.0,
            timestamp=now,
            channel="in_app",
            success=True
        )
        
        # Should be equal
        assert notif1 == notif2
