"""Tests for web interface (Flask routes)."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.web import create_app
from src.notifications.models import Notification


@pytest.fixture
def web_app():
    """Create test Flask app with mocked manager."""
    mock_manager = MagicMock()
    app = create_app(mock_manager)
    app.testing = True
    client = app.test_client()
    return app, client, mock_manager


class TestWebRoutes:
    """Test Flask web routes."""

    def test_index_route_returns_200(self, web_app):
        """Test that index route returns 200 OK."""
        app, client, manager = web_app
        response = client.get("/")
        assert response.status_code == 200

    def test_index_route_returns_html(self, web_app):
        """Test that index route returns HTML content."""
        app, client, manager = web_app
        response = client.get("/")
        assert response.content_type == "text/html; charset=utf-8"

    def test_api_status_route_returns_json(self, web_app):
        """Test that /api/status returns JSON."""
        app, client, manager = web_app
        manager.get_status.return_value = {
            "hge_signal": None,
            "commander_location": None,
            "distance": None,
        }
        
        response = client.get("/api/status")
        assert response.status_code == 200
        assert response.content_type == "application/json"

    def test_api_status_returns_status_data(self, web_app):
        """Test that /api/status returns correct data."""
        app, client, manager = web_app
        expected_status = {
            "hge_signal": {
                "system_name": "Test",
                "age": "5m"
            },
            "commander_location": {
                "system_name": "Sol"
            },
            "distance": {
                "formatted": "50 ly"
            },
        }
        manager.get_status.return_value = expected_status
        
        response = client.get("/api/status")
        data = response.get_json()
        
        assert data == expected_status

    def test_api_refresh_post_returns_200(self, web_app):
        """Test that /api/refresh POST returns 200."""
        app, client, manager = web_app
        manager.get_status.return_value = {"status": "ok"}
        
        response = client.post("/api/refresh")
        assert response.status_code == 200

    def test_api_refresh_calls_refresh(self, web_app):
        """Test that /api/refresh calls manager.refresh()."""
        app, client, manager = web_app
        manager.get_status.return_value = {"status": "ok"}
        
        client.post("/api/refresh")
        manager.refresh.assert_called_once()

    def test_api_refresh_returns_success_status(self, web_app):
        """Test that /api/refresh returns success status."""
        app, client, manager = web_app
        manager.get_status.return_value = {"status": "ok"}
        
        response = client.post("/api/refresh")
        data = response.get_json()
        
        assert data["status"] == "success"

    def test_api_refresh_returns_current_status(self, web_app):
        """Test that /api/refresh returns current status after refresh."""
        app, client, manager = web_app
        manager.get_status.return_value = {
            "hge_signal": {"system_name": "Updated"}
        }
        
        response = client.post("/api/refresh")
        data = response.get_json()
        
        assert data["data"]["hge_signal"]["system_name"] == "Updated"

    def test_api_refresh_error_handling(self, web_app):
        """Test that /api/refresh handles errors."""
        app, client, manager = web_app
        manager.refresh.side_effect = Exception("Refresh failed")
        
        response = client.post("/api/refresh")
        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "error"

    def test_api_notifications_returns_json(self, web_app):
        """Test that /api/notifications returns JSON."""
        app, client, manager = web_app
        manager.notification_manager.get_notification_history.return_value = []
        
        response = client.get("/api/notifications")
        assert response.status_code == 200
        assert response.content_type == "application/json"

    def test_api_notifications_default_count(self, web_app):
        """Test that /api/notifications uses default count."""
        app, client, manager = web_app
        manager.notification_manager.get_notification_history.return_value = []
        
        client.get("/api/notifications")
        
        # Verify get_notification_history was called with count=10 (default)
        call_args = manager.notification_manager.get_notification_history.call_args
        assert call_args[1]["count"] == 10

    def test_api_notifications_custom_count(self, web_app):
        """Test that /api/notifications respects count parameter."""
        app, client, manager = web_app
        manager.notification_manager.get_notification_history.return_value = []
        
        client.get("/api/notifications?count=5")
        
        # Verify count parameter was used
        call_args = manager.notification_manager.get_notification_history.call_args
        assert call_args[1]["count"] == 5

    def test_api_notifications_returns_success(self, web_app):
        """Test that /api/notifications returns success status."""
        app, client, manager = web_app
        manager.notification_manager.get_notification_history.return_value = []
        
        response = client.get("/api/notifications")
        data = response.get_json()
        
        assert data["status"] == "success"

    def test_api_notifications_returns_notifications(self, web_app):
        """Test that /api/notifications returns notification data."""
        app, client, manager = web_app
        
        notif = Notification(
            signal_system="Test System",
            distance_ly=50.0,
            timestamp=datetime(2025, 10, 22, 12, 0, 0),
            channel="discord",
            success=True,
        )
        manager.notification_manager.get_notification_history.return_value = [notif]
        
        response = client.get("/api/notifications")
        data = response.get_json()
        
        assert len(data["data"]) == 1
        assert data["data"][0]["system_name"] == "Test System"
        assert data["data"][0]["distance_ly"] == 50.0
        assert data["data"][0]["channel"] == "discord"
        assert data["data"][0]["success"] is True

    def test_api_notifications_error_handling(self, web_app):
        """Test that /api/notifications handles errors."""
        app, client, manager = web_app
        manager.notification_manager.get_notification_history.side_effect = Exception("DB Error")
        
        response = client.get("/api/notifications")
        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "error"

    def test_api_notifications_stats_returns_json(self, web_app):
        """Test that /api/notifications/stats returns JSON."""
        app, client, manager = web_app
        manager.notification_manager.get_stats.return_value = {
            "total": 0,
            "successful": 0,
            "failed": 0,
        }
        
        response = client.get("/api/notifications/stats")
        assert response.status_code == 200
        assert response.content_type == "application/json"

    def test_api_notifications_stats_returns_success(self, web_app):
        """Test that /api/notifications/stats returns success status."""
        app, client, manager = web_app
        manager.notification_manager.get_stats.return_value = {
            "total": 0,
            "successful": 0,
            "failed": 0,
        }
        
        response = client.get("/api/notifications/stats")
        data = response.get_json()
        
        assert data["status"] == "success"

    def test_api_notifications_stats_returns_statistics(self, web_app):
        """Test that /api/notifications/stats returns statistics."""
        app, client, manager = web_app
        manager.notification_manager.get_stats.return_value = {
            "total": 10,
            "successful": 8,
            "failed": 2,
        }
        
        response = client.get("/api/notifications/stats")
        data = response.get_json()
        
        assert data["data"]["total"] == 10
        assert data["data"]["successful"] == 8
        assert data["data"]["failed"] == 2

    def test_api_notifications_stats_error_handling(self, web_app):
        """Test that /api/notifications/stats handles errors."""
        app, client, manager = web_app
        manager.notification_manager.get_stats.side_effect = Exception("Stats error")
        
        response = client.get("/api/notifications/stats")
        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "error"

    def test_api_notifications_clear_returns_200(self, web_app):
        """Test that /api/notifications/clear returns 200."""
        app, client, manager = web_app
        
        response = client.post("/api/notifications/clear")
        assert response.status_code == 200

    def test_api_notifications_clear_returns_success(self, web_app):
        """Test that /api/notifications/clear returns success status."""
        app, client, manager = web_app
        
        response = client.post("/api/notifications/clear")
        data = response.get_json()
        
        assert data["status"] == "success"

    def test_api_notifications_clear_calls_clear_history(self, web_app):
        """Test that /api/notifications/clear calls clear_history."""
        app, client, manager = web_app
        
        client.post("/api/notifications/clear")
        manager.notification_manager.in_app.clear_history.assert_called_once()

    def test_api_notifications_clear_error_handling(self, web_app):
        """Test that /api/notifications/clear handles errors."""
        app, client, manager = web_app
        manager.notification_manager.in_app.clear_history.side_effect = Exception("Clear error")
        
        response = client.post("/api/notifications/clear")
        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "error"

    def test_api_notifications_with_error_field(self, web_app):
        """Test that notification error field is included."""
        app, client, manager = web_app
        
        notif = Notification(
            signal_system="Test",
            distance_ly=50.0,
            timestamp=datetime.now(),
            channel="discord",
            success=False,
            error="Connection timeout",
        )
        manager.notification_manager.get_notification_history.return_value = [notif]
        
        response = client.get("/api/notifications")
        data = response.get_json()
        
        assert data["data"][0]["error"] == "Connection timeout"

    def test_notifications_dashboard_page_returns_200(self, web_app):
        """Test that /notifications dashboard page returns 200."""
        app, client, manager = web_app
        
        response = client.get("/notifications")
        assert response.status_code == 200

    def test_notifications_dashboard_returns_html(self, web_app):
        """Test that /notifications dashboard returns HTML."""
        app, client, manager = web_app
        
        response = client.get("/notifications")
        assert response.content_type == "text/html; charset=utf-8"

    def test_multiple_notifications_in_response(self, web_app):
        """Test that multiple notifications are returned correctly."""
        app, client, manager = web_app
        
        notifs = [
            Notification(
                signal_system=f"System {i}",
                distance_ly=50.0 + i,
                timestamp=datetime.now(),
                channel="discord",
                success=True,
            )
            for i in range(5)
        ]
        manager.notification_manager.get_notification_history.return_value = notifs
        
        response = client.get("/api/notifications")
        data = response.get_json()
        
        assert len(data["data"]) == 5
        for i, notif_data in enumerate(data["data"]):
            assert notif_data["system_name"] == f"System {i}"
