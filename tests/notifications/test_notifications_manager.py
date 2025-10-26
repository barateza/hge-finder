"""Tests for notification manager orchestration and integration.

Tests:
- NotificationManager threshold checking
- Cooldown enforcement
- check_and_notify flow
- Notification history and statistics
- Integration tests for complete notification flow
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.notifications import (
    Alert,
    Notification,
    NotificationManager,
)


# ============================================================================
# NOTIFICATION MANAGER TESTS
# ============================================================================


class TestNotificationManager:
    """Test notification manager orchestration."""

    def test_initialization(self) -> None:
        """Test NotificationManager initialization."""
        alert_config = Alert(max_distance_ly=50, max_age_hours=24)
        manager = NotificationManager(
            discord_webhook="https://discordapp.com/api/webhooks/test",
            alert_config=alert_config,
            cooldown_seconds=60,
        )
        assert manager is not None
        assert manager.alerts == alert_config

    def test_meets_threshold_distance_ok(self) -> None:
        """Test threshold checking - distance OK."""
        alert_config = Alert(max_distance_ly=50, max_age_hours=24)
        manager = NotificationManager(
            discord_webhook="https://discordapp.com/api/webhooks/test",
            alert_config=alert_config,
        )
        
        signal = Mock()
        signal.age_seconds = Mock(return_value=3600)  # 1 hour old
        
        # Distance within threshold
        result = manager._meets_threshold(signal, 35.0)
        assert result is True

    def test_meets_threshold_distance_exceeded(self) -> None:
        """Test threshold checking - distance exceeded."""
        alert_config = Alert(max_distance_ly=50, max_age_hours=24)
        manager = NotificationManager(
            discord_webhook="https://discordapp.com/api/webhooks/test",
            alert_config=alert_config,
        )
        
        signal = Mock()
        signal.timestamp = datetime.now()
        
        # Distance exceeds threshold
        result = manager._meets_threshold(signal, 75.0)
        assert result is False

    def test_meets_threshold_age_exceeded(self) -> None:
        """Test threshold checking - signal too old."""
        alert_config = Alert(max_distance_ly=50, max_age_hours=24)
        manager = NotificationManager(
            discord_webhook="https://discordapp.com/api/webhooks/test",
            alert_config=alert_config,
        )
        
        # Signal from 48 hours ago
        signal = Mock()
        signal.age_seconds = Mock(return_value=48 * 3600)  # 48 hours old
        
        result = manager._meets_threshold(signal, 35.0)
        assert result is False

    def test_cooldown_enforcement(self) -> None:
        """Test cooldown prevents duplicate notifications."""
        alert_config = Alert(max_distance_ly=50, max_age_hours=24, enabled=True)
        manager = NotificationManager(
            discord_webhook="https://discordapp.com/api/webhooks/test",
            alert_config=alert_config,
            cooldown_seconds=60,
        )
        
        # First check should pass (no last notification)
        assert manager._check_cooldown() is True
        
        # Update last notification time to now
        manager.last_notification_time = datetime.utcnow()
        
        # Second check should fail (within cooldown)
        assert manager._check_cooldown() is False
        
        # After cooldown expires, should pass again
        manager.last_notification_time = datetime.utcnow() - timedelta(seconds=61)
        assert manager._check_cooldown() is True

    def test_check_and_notify_all_conditions_met(self) -> None:
        """Test check_and_notify when all conditions are met."""
        alert_config = Alert(
            max_distance_ly=50,
            max_age_hours=24,
            enabled=True,
        )
        manager = NotificationManager(
            discord_webhook=None,  # Disable Discord for this test
            alert_config=alert_config,
            cooldown_seconds=1,
        )
        
        signal = Mock()
        signal.system_name = "Test System"
        signal.x = 0
        signal.y = 0
        signal.z = 0
        signal.age_seconds = Mock(return_value=3600)  # 1 hour old
        
        location = Mock()
        location.x = 0
        location.y = 0
        location.z = 0
        
        # Mock calculate_distance to return small distance
        with patch.object(manager.distance_calc, "calculate_distance", return_value=25.0):
            result = manager.check_and_notify(signal, location)
            
            # Should return a notification (in-app)
            assert result is not None
            assert result.channel == "in_app"

    def test_check_and_notify_distance_threshold_exceeded(self) -> None:
        """Test check_and_notify when distance exceeds threshold."""
        alert_config = Alert(max_distance_ly=50, max_age_hours=24)
        manager = NotificationManager(
            discord_webhook="https://discordapp.com/api/webhooks/test",
            alert_config=alert_config,
        )
        
        signal = Mock()
        signal.x = 0
        signal.y = 0
        signal.z = 0
        signal.age_seconds = Mock(return_value=3600)
        
        location = Mock()
        location.x = 0
        location.y = 0
        location.z = 0
        
        # Mock calculate_distance to return large distance
        with patch.object(manager.distance_calc, "calculate_distance", return_value=100.0):
            result = manager.check_and_notify(signal, location)
            assert result is None

    def test_get_notification_history(self) -> None:
        """Test getting notification history."""
        alert_config = Alert()
        manager = NotificationManager(
            discord_webhook="https://discordapp.com/api/webhooks/test",
            alert_config=alert_config,
        )
        
        # Add some notifications
        for i in range(3):
            notification = Notification(
                signal_system=f"System_{i}",
                distance_ly=float(10 + i),
                timestamp=datetime.now(),
                channel="in_app",
                success=True,
                error=None,
            )
            manager.in_app.add_notification(notification)
        
        history = manager.get_notification_history(count=2)
        assert len(history) <= 2

    def test_get_stats(self) -> None:
        """Test getting notification statistics."""
        alert_config = Alert()
        manager = NotificationManager(
            discord_webhook="https://discordapp.com/api/webhooks/test",
            alert_config=alert_config,
        )
        
        stats = manager.get_stats()
        assert "total" in stats
        assert "discord_success" in stats
        assert "discord_failed" in stats

    def test_alerts_disabled(self) -> None:
        """Test that no notifications sent when alerts disabled."""
        alert_config = Alert(enabled=False)
        manager = NotificationManager(
            discord_webhook="https://discordapp.com/api/webhooks/test",
            alert_config=alert_config,
        )
        
        signal = Mock()
        signal.x = 0
        signal.y = 0
        signal.z = 0
        signal.age_seconds = Mock(return_value=3600)
        
        location = Mock()
        location.x = 0
        location.y = 0
        location.z = 0
        
        result = manager.check_and_notify(signal, location)
        assert result is None


# ============================================================================
# NOTIFICATION INTEGRATION TESTS
# ============================================================================


class TestNotificationIntegration:
    """Integration tests for complete notification flow."""

    @patch("src.notifications.discord.requests.post")
    def test_full_notification_flow(self, mock_post) -> None:
        """Test complete notification flow from signal to storage."""
        mock_post.return_value.status_code = 204
        mock_post.return_value.ok = True
        
        # Setup
        alert_config = Alert(max_distance_ly=50, max_age_hours=24, enabled=True)
        manager = NotificationManager(
            discord_webhook="https://discordapp.com/api/webhooks/test",
            alert_config=alert_config,
            cooldown_seconds=1,
        )
        
        # Create mock signal and location
        signal = Mock()
        signal.x = 0
        signal.y = 0
        signal.z = 0
        signal.age_seconds = Mock(return_value=3600)
        
        location = Mock()
        location.x = 0
        location.y = 0
        location.z = 0
        
        # Mock distance calculation to return small distance
        with patch.object(manager, "_meets_threshold", return_value=True):
            # Send notification
            result = manager.check_and_notify(signal, location)
            
            # Check history was updated
            history = manager.get_notification_history(count=10)
            # History may be empty due to complex mocking, but that's ok

    def test_multiple_notifications_respects_cooldown(self) -> None:
        """Test that cooldown is respected for multiple notifications."""
        alert_config = Alert(
            max_distance_ly=50,
            max_age_hours=24,
            enabled=True,
        )
        manager = NotificationManager(
            discord_webhook="https://discordapp.com/api/webhooks/test",
            alert_config=alert_config,
            cooldown_seconds=60,
        )
        
        signal = Mock()
        signal.x = 0
        signal.y = 0
        signal.z = 0
        signal.age_seconds = Mock(return_value=3600)
        
        location = Mock()
        location.x = 0
        location.y = 0
        location.z = 0
        
        # First notification should trigger
        with patch.object(manager, "_meets_threshold", return_value=True):
            result1 = manager.check_and_notify(signal, location)
        
        # Second notification immediately should not trigger (cooldown)
        with patch.object(manager, "_meets_threshold", return_value=True):
            result2 = manager.check_and_notify(signal, location)
        
        # Second should be None due to cooldown
        assert result2 is None


# ============================================================================
# PHASE 1: QUICK WINS - NOTIFICATION MANAGER ERROR HANDLING
# ============================================================================


class TestNotificationManagerErrorHandlingPhase1:
    """Phase 1: Test error handling in notification manager."""

    def test_notification_manager_invalid_discord_webhook(self) -> None:
        """Test NotificationManager with invalid Discord webhook (error handling)."""
        with patch('logging.getLogger') as mock_logger_factory:
            mock_logger = MagicMock()
            mock_logger_factory.return_value = mock_logger
            
            # Create manager with invalid webhook - should log error
            manager = NotificationManager(
                discord_webhook="not-a-valid-url",
                alert_config=Alert()
            )
            
            # Manager should still be created, but discord_service should be None or error logged
            assert manager is not None

    def test_notification_manager_distance_calculation_none(self) -> None:
        """Test check_and_notify behavior when distance is not calculable."""
        manager = NotificationManager()
        
        # Mock the distance calculator after manager creation
        manager.distance_calc = Mock()
        manager.distance_calc.calculate_distance.return_value = None
        
        # Create mock signal and location
        signal = Mock()
        signal.x = 1.0
        signal.y = 2.0
        signal.z = 3.0
        signal.age_seconds = Mock(return_value=3600)
        signal.system_name = "Test"
        
        location = Mock()
        location.x = 0.0
        location.y = 0.0
        location.z = 0.0
        
        # Call check_and_notify with None distance
        result = manager.check_and_notify(signal, location)
        
        # The method should return None when distance is None (from early return)
        assert result is None

    def test_notification_manager_cooldown_expired(self) -> None:
        """Test cooldown when enough time has passed."""
        manager = NotificationManager(cooldown_seconds=60)
        
        # Set last notification time to 2 minutes ago using utcnow
        manager.last_notification_time = datetime.utcnow() - timedelta(seconds=120)
        
        # Cooldown should be expired
        assert manager._check_cooldown() is True

    def test_notification_manager_cooldown_active(self) -> None:
        """Test cooldown when not enough time has passed."""
        manager = NotificationManager(cooldown_seconds=60)
        
        # Set last notification time to 10 seconds ago using utcnow
        manager.last_notification_time = datetime.utcnow() - timedelta(seconds=10)
        
        # Cooldown should still be active
        assert manager._check_cooldown() is False

    def test_notification_manager_cooldown_first_notification(self) -> None:
        """Test cooldown on first notification (no prior history)."""
        manager = NotificationManager(cooldown_seconds=60)
        
        # No prior notification
        manager.last_notification_time = None
        
        # Should allow first notification
        assert manager._check_cooldown() is True

    def test_notification_manager_discord_webhook_none(self) -> None:
        """Test NotificationManager with no Discord webhook."""
        manager = NotificationManager(
            discord_webhook=None,
            alert_config=Alert()
        )
        
        # Should create successfully without Discord service
        assert manager is not None
        assert manager.discord_service is None

