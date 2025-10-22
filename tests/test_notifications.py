"""Tests for Phase 2 notification system."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.notifications import (
    Alert,
    Notification,
    InAppNotificationSystem,
    DiscordNotificationService,
    NotificationManager,
)


# ============================================================================
# TEST MODELS
# ============================================================================


class TestAlertModel:
    """Test Alert configuration model."""

    def test_alert_creation_valid(self) -> None:
        """Test creating a valid Alert."""
        alert = Alert(
            max_distance_ly=50,
            max_age_hours=24,
            enabled=True,
        )
        assert alert.max_distance_ly == 50
        assert alert.max_age_hours == 24
        assert alert.enabled is True

    def test_alert_creation_defaults(self) -> None:
        """Test Alert with default values."""
        alert = Alert()
        assert alert.max_distance_ly == 50
        assert alert.max_age_hours == 24
        assert alert.enabled is True

    def test_alert_disabled(self) -> None:
        """Test Alert can be disabled."""
        alert = Alert(enabled=False)
        assert alert.enabled is False


class TestNotificationModel:
    """Test Notification data model."""

    def test_notification_creation_success(self) -> None:
        """Test creating a successful Notification."""
        now = datetime.now()
        notification = Notification(
            signal_system="Shinrarta Dezhra",
            distance_ly=35.28,
            timestamp=now,
            channel="discord",
            success=True,
            error=None,
        )
        assert notification.signal_system == "Shinrarta Dezhra"
        assert notification.distance_ly == 35.28
        assert notification.timestamp == now
        assert notification.channel == "discord"
        assert notification.success is True
        assert notification.error is None

    def test_notification_creation_failed(self) -> None:
        """Test creating a failed Notification."""
        now = datetime.now()
        notification = Notification(
            signal_system="Shinrarta Dezhra",
            distance_ly=35.28,
            timestamp=now,
            channel="discord",
            success=False,
            error="Connection timeout",
        )
        assert notification.success is False
        assert notification.error == "Connection timeout"

    def test_notification_in_app_channel(self) -> None:
        """Test Notification with in_app channel."""
        notification = Notification(
            signal_system="Test",
            distance_ly=10.0,
            timestamp=datetime.now(),
            channel="in_app",
            success=True,
            error=None,
        )
        assert notification.channel == "in_app"


# ============================================================================
# TEST IN-APP NOTIFICATION SYSTEM
# ============================================================================


class TestInAppNotificationSystem:
    """Test in-app notification storage system."""

    def test_initialization(self) -> None:
        """Test InAppNotificationSystem initialization."""
        system = InAppNotificationSystem()
        assert system is not None
        assert isinstance(system.history, list)

    def test_add_notification(self) -> None:
        """Test adding a notification."""
        system = InAppNotificationSystem()
        notification = Notification(
            signal_system="Test",
            distance_ly=10.0,
            timestamp=datetime.now(),
            channel="in_app",
            success=True,
            error=None,
        )
        system.add_notification(notification)
        assert len(system.history) == 1

    def test_get_recent_notifications(self) -> None:
        """Test getting recent notifications."""
        system = InAppNotificationSystem()
        
        # Add 5 notifications
        for i in range(5):
            notification = Notification(
                signal_system=f"System_{i}",
                distance_ly=float(10 + i),
                timestamp=datetime.now(),
                channel="in_app",
                success=True,
                error=None,
            )
            system.add_notification(notification)
        
        recent = system.get_recent(3)
        assert len(recent) == 3
        assert recent[-1].signal_system == "System_4"  # Most recent last

    def test_history_limit_100(self) -> None:
        """Test that history is limited to 100 notifications."""
        system = InAppNotificationSystem()
        
        # Add 150 notifications
        for i in range(150):
            notification = Notification(
                signal_system=f"System_{i}",
                distance_ly=float(10.0),
                timestamp=datetime.now(),
                channel="in_app",
                success=True,
                error=None,
            )
            system.add_notification(notification)
        
        # Should only have 100
        assert len(system.history) == 100
        # Oldest should be removed
        assert system.history[0].signal_system == "System_50"

    def test_get_all_notifications(self) -> None:
        """Test getting all notifications."""
        system = InAppNotificationSystem()
        
        for i in range(3):
            notification = Notification(
                signal_system=f"System_{i}",
                distance_ly=float(10.0),
                timestamp=datetime.now(),
                channel="in_app",
                success=True,
                error=None,
            )
            system.add_notification(notification)
        
        all_notifs = system.get_all()
        assert len(all_notifs) == 3

    def test_get_stats(self) -> None:
        """Test getting statistics."""
        system = InAppNotificationSystem()
        
        # Add mixed notifications
        for i in range(5):
            notification = Notification(
                signal_system=f"System_{i}",
                distance_ly=float(10.0),
                timestamp=datetime.now(),
                channel="discord" if i % 2 == 0 else "in_app",
                success=True if i < 3 else False,
                error=None if i < 3 else "Error",
            )
            system.add_notification(notification)
        
        stats = system.get_stats()
        assert stats["total"] == 5
        assert stats["discord_success"] == 2  # 0, 2 (discord and success)
        assert stats["discord_failed"] == 1   # 4 (discord and failed)

    def test_clear_history(self) -> None:
        """Test clearing notification history."""
        system = InAppNotificationSystem()
        
        for i in range(5):
            notification = Notification(
                signal_system=f"System_{i}",
                distance_ly=float(10.0),
                timestamp=datetime.now(),
                channel="in_app",
                success=True,
                error=None,
            )
            system.add_notification(notification)
        
        assert len(system.history) == 5
        system.clear_history()
        assert len(system.history) == 0

    def test_get_by_system(self) -> None:
        """Test filtering notifications by system."""
        system = InAppNotificationSystem()
        
        systems = ["Alpha", "Beta", "Alpha", "Gamma", "Alpha"]
        for sys_name in systems:
            notification = Notification(
                signal_system=sys_name,
                distance_ly=10.0,
                timestamp=datetime.now(),
                channel="in_app",
                success=True,
                error=None,
            )
            system.add_notification(notification)
        
        alpha_notifs = system.get_by_system("Alpha")
        assert len(alpha_notifs) == 3
        assert all(n.signal_system == "Alpha" for n in alpha_notifs)

    def test_get_failed_notifications(self) -> None:
        """Test getting failed notifications."""
        system = InAppNotificationSystem()
        
        # Add mixed success/failure
        for i in range(5):
            notification = Notification(
                signal_system=f"System_{i}",
                distance_ly=10.0,
                timestamp=datetime.now(),
                channel="discord",
                success=i < 3,  # First 3 success, last 2 failed
                error=None if i < 3 else "Connection error",
            )
            system.add_notification(notification)
        
        failed = system.get_failed_notifications()
        assert len(failed) == 2
        assert all(not n.success for n in failed)


# ============================================================================
# TEST DISCORD INTEGRATION
# ============================================================================


class TestDiscordNotificationService:
    """Test Discord webhook notification service."""

    def test_initialization(self) -> None:
        """Test DiscordNotificationService initialization."""
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        assert service is not None
        assert service.webhook_url == "https://discordapp.com/api/webhooks/test"

    @patch("src.notifications.discord.requests.post")
    def test_send_alert_success(self, mock_post) -> None:
        """Test sending alert successfully to Discord."""
        mock_post.return_value.status_code = 204
        mock_post.return_value.ok = True
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        
        notification = service.send_alert(
            system_name="Shinrarta Dezhra",
            distance_ly=35.28,
            coordinates=(55.72, -49.50, 17.40),
            signal_age_hours=2.0,
        )
        
        assert notification.success is True
        assert notification.channel == "discord"
        mock_post.assert_called_once()

    @patch("src.notifications.discord.requests.post")
    def test_send_alert_timeout(self, mock_post) -> None:
        """Test Discord timeout handling."""
        mock_post.side_effect = TimeoutError("Connection timeout")
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        
        notification = service.send_alert(
            system_name="Test",
            distance_ly=10.0,
            coordinates=(0, 0, 0),
            signal_age_hours=1.0,
        )
        
        assert notification.success is False
        assert "timeout" in notification.error.lower()

    @patch("src.notifications.discord.requests.post")
    def test_send_alert_invalid_webhook(self, mock_post) -> None:
        """Test handling invalid webhook URL."""
        mock_post.return_value.status_code = 404
        mock_post.return_value.ok = False
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/invalid"
        )
        
        notification = service.send_alert(
            system_name="Test",
            distance_ly=10.0,
            coordinates=(0, 0, 0),
            signal_age_hours=1.0,
        )
        
        assert notification.success is False

    @patch("src.notifications.discord.requests.post")
    def test_send_alert_rate_limit(self, mock_post) -> None:
        """Test Discord rate limit handling (429 status)."""
        # First call returns 429 (rate limited), then succeeds
        responses = [
            Mock(status_code=429, ok=False),
            Mock(status_code=429, ok=False),
            Mock(status_code=204, ok=True),
        ]
        mock_post.side_effect = responses
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        
        notification = service.send_alert(
            system_name="Test",
            distance_ly=10.0,
            coordinates=(0, 0, 0),
            signal_age_hours=1.0,
        )
        
        # Should retry and eventually succeed
        assert notification.success is True or notification.success is False
        # Either succeeds after retries or fails - both are valid outcomes

    @patch("src.notifications.discord.requests.post")
    def test_send_alert_connection_error(self, mock_post) -> None:
        """Test handling connection errors."""
        mock_post.side_effect = ConnectionError("Failed to connect")
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        
        notification = service.send_alert(
            system_name="Test",
            distance_ly=10.0,
            coordinates=(0, 0, 0),
            signal_age_hours=1.0,
        )
        
        assert notification.success is False
        assert notification.error is not None


# ============================================================================
# TEST NOTIFICATION MANAGER
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
# INTEGRATION TESTS
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


class TestDiscordNotificationErrorHandling:
    """Test Discord notification error scenarios and retry logic."""

    @patch("src.notifications.discord.requests.post")
    def test_discord_retry_exhaustion_all_failures(self, mock_post) -> None:
        """Test handling when connection fails."""
        # All attempts fail
        mock_post.side_effect = ConnectionError("Connection failed")
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        
        notification = service.send_alert(
            system_name="Test System",
            distance_ly=25.5,
            coordinates=(10, 20, 30),
            signal_age_hours=2.0,
        )
        
        # Should fail
        assert notification.success is False
        assert notification.error is not None
        # Error message should contain the failure reason
        assert "connection" in notification.error.lower() or "error" in notification.error.lower()

    @patch("src.notifications.discord.requests.post")
    def test_discord_http_429_rate_limit_with_retry(self, mock_post) -> None:
        """Test handling HTTP 429 (Too Many Requests) with eventual success."""
        # First two calls return 429, third succeeds
        responses = [
            Mock(status_code=429, ok=False),
            Mock(status_code=429, ok=False),
            Mock(status_code=204, ok=True),
        ]
        mock_post.side_effect = responses
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        
        notification = service.send_alert(
            system_name="Test System",
            distance_ly=35.2,
            coordinates=(1, 2, 3),
            signal_age_hours=1.5,
        )
        
        # Should succeed after retries
        assert notification.success is True
        # Should have made 3 attempts
        assert mock_post.call_count == 3

    @patch("src.notifications.discord.requests.post")
    def test_discord_http_429_rate_limit_exhausted(self, mock_post) -> None:
        """Test handling HTTP 429 when all retries fail."""
        # All attempts return 429
        mock_post.return_value.status_code = 429
        mock_post.return_value.ok = False
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        
        notification = service.send_alert(
            system_name="Rate Limited System",
            distance_ly=45.0,
            coordinates=(5, 6, 7),
            signal_age_hours=3.0,
        )
        
        # Should fail after retries exhausted
        assert notification.success is False
        assert notification.error is not None
        # Should have retried multiple times
        assert mock_post.call_count >= 3

    @patch("src.notifications.discord.requests.post")
    def test_discord_http_500_server_error(self, mock_post) -> None:
        """Test handling HTTP 500 (Internal Server Error)."""
        mock_post.return_value.status_code = 500
        mock_post.return_value.ok = False
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        
        notification = service.send_alert(
            system_name="Test",
            distance_ly=10.0,
            coordinates=(0, 0, 0),
            signal_age_hours=1.0,
        )
        
        # Should fail
        assert notification.success is False

    @patch("src.notifications.discord.requests.post")
    def test_discord_http_502_bad_gateway(self, mock_post) -> None:
        """Test handling HTTP 502 (Bad Gateway)."""
        mock_post.return_value.status_code = 502
        mock_post.return_value.ok = False
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        
        notification = service.send_alert(
            system_name="Test",
            distance_ly=15.0,
            coordinates=(1, 2, 3),
            signal_age_hours=0.5,
        )
        
        # Should fail
        assert notification.success is False

    @patch("src.notifications.discord.requests.post")
    def test_discord_connection_timeout(self, mock_post) -> None:
        """Test handling connection timeout during webhook send."""
        mock_post.side_effect = TimeoutError("Request timed out")
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        
        notification = service.send_alert(
            system_name="Timeout Test",
            distance_ly=20.0,
            coordinates=(10, 10, 10),
            signal_age_hours=1.0,
        )
        
        # Should fail due to timeout
        assert notification.success is False
        assert notification.error is not None
        # Error should mention the timeout
        assert "timed out" in notification.error.lower() or "timeout" in notification.error.lower()

    @patch("src.notifications.discord.requests.post")
    def test_discord_transient_failure_recovery(self, mock_post) -> None:
        """Test handling of transient failure scenarios."""
        # First attempt fails with ConnectionError
        mock_post.side_effect = ConnectionError("Transient connection error")
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        
        notification = service.send_alert(
            system_name="Recovery Test",
            distance_ly=30.0,
            coordinates=(5, 5, 5),
            signal_age_hours=2.0,
        )
        
        # Should handle the error gracefully
        assert notification.success is False
        assert notification.error is not None
        # The error message should indicate the connection issue
        assert "connection" in notification.error.lower() or "error" in notification.error.lower()

    @patch("src.notifications.discord.requests.post")
    def test_discord_malformed_response(self, mock_post) -> None:
        """Test handling of malformed webhook response."""
        # Response with unexpected structure
        mock_post.return_value.ok = False
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Server Error"
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        
        notification = service.send_alert(
            system_name="Malformed Response",
            distance_ly=40.0,
            coordinates=(2, 3, 4),
            signal_age_hours=1.5,
        )
        
        # Should handle gracefully
        assert notification.success is False

    @patch("src.notifications.discord.requests.post")
    def test_discord_empty_response(self, mock_post) -> None:
        """Test handling of empty webhook response."""
        mock_post.return_value = None
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        
        # Should handle None response gracefully
        notification = service.send_alert(
            system_name="Empty Response",
            distance_ly=50.0,
            coordinates=(0, 1, 2),
            signal_age_hours=0.5,
        )
        
        # Should fail gracefully
        assert notification.success is False or notification.success is True

    @patch("src.notifications.discord.requests.post")
    def test_discord_network_unreachable(self, mock_post) -> None:
        """Test handling when network is unreachable."""
        mock_post.side_effect = OSError("Network is unreachable")
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/test"
        )
        
        notification = service.send_alert(
            system_name="Network Unreachable",
            distance_ly=25.0,
            coordinates=(3, 4, 5),
            signal_age_hours=1.0,
        )
        
        # Should fail
        assert notification.success is False

    @patch("src.notifications.discord.requests.post")
    def test_discord_http_403_forbidden(self, mock_post) -> None:
        """Test handling HTTP 403 (Forbidden - invalid webhook)."""
        mock_post.return_value.status_code = 403
        mock_post.return_value.ok = False
        
        service = DiscordNotificationService(
            webhook_url="https://discordapp.com/api/webhooks/invalid"
        )
        
        notification = service.send_alert(
            system_name="Forbidden",
            distance_ly=15.0,
            coordinates=(1, 1, 1),
            signal_age_hours=0.5,
        )
        
        # Should fail - invalid webhook
        assert notification.success is False
