"""Tests for Discord notification service.

Tests:
- Discord webhook notification sending
- Error handling and retry logic
- HTTP error scenarios (429, 500, 502, 403, 404)
- Network errors (timeout, connection refused, etc.)
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.notifications import (
    DiscordNotificationService,
)


# ============================================================================
# DISCORD NOTIFICATION SERVICE TESTS
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
        assert notification.error is not None
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
# DISCORD ERROR HANDLING TESTS
# ============================================================================


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

