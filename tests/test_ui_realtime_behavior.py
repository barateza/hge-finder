"""Tests for UI real-time behavior optimization (Task 8).

Tests conditional polling, real-time updates, and graceful fallback
from WebSocket to REST API polling.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from src.web import create_app
from src.web.websocket import WebSocketManager
from src.core import HGENotifierManager


class TestUIRealtimeBehavior:
    """Test UI real-time behavior optimizations."""

    def test_polling_disabled_when_connected(self):
        """Verify polling timer is cleared when WebSocket connects."""
        # This test validates the JavaScript logic by checking the HTML includes
        # the polling timer management code
        from src.web import HTML_TEMPLATE
        
        assert "pollingTimer = null" in HTML_TEMPLATE
        assert "clearInterval(pollingTimer)" in HTML_TEMPLATE
        assert "Polling stopped - using real-time updates" in HTML_TEMPLATE
    
    def test_polling_enabled_when_disconnected(self):
        """Verify polling timer is started when WebSocket disconnects."""
        from src.web import HTML_TEMPLATE
        
        assert "pollingTimer = setInterval(updateStatusViaREST" in HTML_TEMPLATE
        assert "Starting fallback polling" in HTML_TEMPLATE
        assert "POLLING_INTERVAL_MS = 30000" in HTML_TEMPLATE
    
    def test_polling_interval_dashboard(self):
        """Verify dashboard polling interval is 30 seconds."""
        from src.web import HTML_TEMPLATE
        
        # Dashboard should use 30s polling
        assert "POLLING_INTERVAL_MS = 30000" in HTML_TEMPLATE
        assert "30 seconds fallback polling" in HTML_TEMPLATE
    
    def test_polling_interval_notifications(self):
        """Verify notifications polling interval is 10 seconds."""
        from src.web import NOTIFICATIONS_TEMPLATE
        
        # Notifications should use 10s polling
        assert "NOTIFICATIONS_POLLING_INTERVAL_MS = 10000" in NOTIFICATIONS_TEMPLATE
        assert "10 seconds fallback polling" in NOTIFICATIONS_TEMPLATE
    
    def test_immediate_refresh_on_disconnect(self):
        """Verify immediate data refresh on disconnect before polling starts."""
        from src.web import HTML_TEMPLATE
        
        # Should immediately call updateStatusViaREST without waiting for interval
        assert "updateStatusViaREST()" in HTML_TEMPLATE
        assert "Immediate refresh to avoid waiting for first interval" in HTML_TEMPLATE
    
    def test_rest_update_function_exists(self):
        """Verify REST API update function is defined."""
        from src.web import HTML_TEMPLATE
        
        assert "function updateStatusViaREST()" in HTML_TEMPLATE
        assert "fetch(statusEndpoint)" in HTML_TEMPLATE
        assert "renderStatus(data)" in HTML_TEMPLATE


class TestDashboardRealtime:
    """Test dashboard real-time update behavior."""
    
    def test_websocket_event_listeners(self):
        """Verify dashboard has all WebSocket event listeners."""
        from src.web import HTML_TEMPLATE
        
        # Check for all 4 channel listeners
        assert "socket.on('hge_signal_update'" in HTML_TEMPLATE
        assert "socket.on('location_update'" in HTML_TEMPLATE
        assert "socket.on('distance_update'" in HTML_TEMPLATE
        assert "socket.on('status_update'" in HTML_TEMPLATE
    
    def test_initial_load_via_rest(self):
        """Verify initial load uses REST API, not polling."""
        from src.web import HTML_TEMPLATE
        
        # Should call updateStatusViaREST on initial load
        assert "updateStatusViaREST();" in HTML_TEMPLATE
        # Should NOT have old polling setup
        assert "setInterval(updateStatus, 30000)" not in HTML_TEMPLATE
    
    def test_refresh_button_works_regardless_of_connection(self):
        """Verify refresh button works with both WebSocket and REST."""
        from src.web import HTML_TEMPLATE
        
        # Refresh should always work
        assert "function refreshStatus()" in HTML_TEMPLATE
        assert "fetch(refreshEndpoint" in HTML_TEMPLATE
        assert "renderStatus(data.data)" in HTML_TEMPLATE
    
    def test_connection_status_indicator(self):
        """Verify connection status indicator updates."""
        from src.web import HTML_TEMPLATE
        
        assert "updateConnectionStatus(true)" in HTML_TEMPLATE
        assert "updateConnectionStatus(false)" in HTML_TEMPLATE
        assert "status-indicator" in HTML_TEMPLATE


class TestNotificationsRealtime:
    """Test notifications page real-time update behavior."""
    
    def test_notifications_polling_timer_management(self):
        """Verify notifications polling timer is properly managed."""
        from src.web import NOTIFICATIONS_TEMPLATE
        
        assert "notificationsPollingTimer = null" in NOTIFICATIONS_TEMPLATE
        assert "clearInterval(notificationsPollingTimer)" in NOTIFICATIONS_TEMPLATE
        assert "notificationsPollingTimer = setInterval(loadNotifications" in NOTIFICATIONS_TEMPLATE
    
    def test_notifications_immediate_load_on_disconnect(self):
        """Verify notifications immediately load on disconnect."""
        from src.web import NOTIFICATIONS_TEMPLATE
        
        # Should immediately call loadNotifications without waiting
        assert "loadNotifications();" in NOTIFICATIONS_TEMPLATE
    
    def test_notifications_status_channel_subscription(self):
        """Verify notifications subscribe to status channel only."""
        from src.web import NOTIFICATIONS_TEMPLATE
        
        assert "channels: ['status']" in NOTIFICATIONS_TEMPLATE
        # Should listen for status updates
        assert "socket.on('status_update'" in NOTIFICATIONS_TEMPLATE


class TestPollingFallback:
    """Test fallback polling behavior when WebSocket is unavailable."""
    
    def test_rest_api_fallback_error_handling(self):
        """Verify REST API fallback handles errors gracefully."""
        from src.web import HTML_TEMPLATE
        
        # Should have error handling
        assert ".catch(error =>" in HTML_TEMPLATE
        assert "Error fetching status via REST" in HTML_TEMPLATE
    
    def test_rest_api_checks_response_status(self):
        """Verify REST API fallback checks HTTP status."""
        from src.web import HTML_TEMPLATE
        
        assert "if (!response.ok)" in HTML_TEMPLATE
        assert "HTTP error! status" in HTML_TEMPLATE
    
    def test_polling_only_when_disconnected(self):
        """Verify polling only runs when WebSocket is disconnected."""
        from src.web import HTML_TEMPLATE
        
        # Polling logic should check connection status
        assert "if (!isConnected)" not in HTML_TEMPLATE  # Old code removed
        # New code: polling is controlled by connect/disconnect handlers
        assert "if (pollingTimer === null)" in HTML_TEMPLATE


class TestAPIEndpoints:
    """Test REST API endpoints for real-time updates."""
    
    @pytest.fixture
    def manager(self):
        """Create test manager."""
        return Mock(spec=HGENotifierManager)
    
    @pytest.fixture
    def app(self, manager):
        """Create Flask app for testing."""
        return create_app(manager)
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_api_status_endpoint_exists(self, client):
        """Verify /api/status endpoint exists."""
        # This should work even without full manager setup
        # (may return error but endpoint should exist)
        response = client.get('/api/status')
        # Should not be 404
        assert response.status_code != 404
    
    def test_api_refresh_endpoint_exists(self, client):
        """Verify /api/refresh endpoint exists."""
        response = client.post('/api/refresh')
        assert response.status_code != 404
    
    def test_api_notifications_endpoint_exists(self, client):
        """Verify /api/notifications endpoint exists."""
        response = client.get('/api/notifications')
        assert response.status_code != 404


class TestPerformanceOptimizations:
    """Test performance optimizations for real-time updates."""
    
    def test_no_unnecessary_polling(self):
        """Verify no polling when WebSocket is connected."""
        from src.web import HTML_TEMPLATE
        
        # Timer should be cleared on connect, not left running
        assert "clearInterval(pollingTimer)" in HTML_TEMPLATE
        assert "pollingTimer = null" in HTML_TEMPLATE
    
    def test_reduced_polling_frequency_when_disconnected(self):
        """Verify polling frequency is reasonable."""
        from src.web import HTML_TEMPLATE
        
        # Dashboard: 30 seconds is reasonable
        assert "30000" in HTML_TEMPLATE
        
        from src.web import NOTIFICATIONS_TEMPLATE
        # Notifications: 10 seconds is reasonable
        assert "10000" in NOTIFICATIONS_TEMPLATE
    
    def test_connection_state_tracking(self):
        """Verify connection state is properly tracked."""
        from src.web import HTML_TEMPLATE
        
        assert "let isConnected = false" in HTML_TEMPLATE
        assert "isConnected = true" in HTML_TEMPLATE
        assert "isConnected = false" in HTML_TEMPLATE


class TestEdgeCases:
    """Test edge cases in real-time behavior."""
    
    def test_multiple_disconnect_events(self):
        """Verify polling doesn't start twice on multiple disconnects."""
        from src.web import HTML_TEMPLATE
        
        # Check is present to prevent double-polling
        assert "if (pollingTimer === null)" in HTML_TEMPLATE
    
    def test_multiple_connect_events(self):
        """Verify polling doesn't stop twice on multiple connects."""
        from src.web import HTML_TEMPLATE
        
        # Check is present to prevent clearing already-null timer
        assert "if (pollingTimer !== null)" in HTML_TEMPLATE
    
    def test_refresh_button_during_polling(self):
        """Verify refresh button works while polling."""
        from src.web import HTML_TEMPLATE
        
        # Refresh function should work independently
        assert "function refreshStatus()" in HTML_TEMPLATE
        assert "refreshEndpoint" in HTML_TEMPLATE
    
    def test_connection_error_handling(self):
        """Verify connection errors are handled gracefully."""
        from src.web import HTML_TEMPLATE
        
        assert "socket.on('connect_error'" in HTML_TEMPLATE
        assert "updateConnectionStatus(false)" in HTML_TEMPLATE


class TestMobilePerformance:
    """Test mobile-specific performance optimizations."""
    
    def test_reduced_update_frequency_on_mobile(self):
        """Verify polling is reasonable for mobile networks."""
        # 30 seconds for dashboard is reasonable
        # 10 seconds for notifications is reasonable
        from src.web import HTML_TEMPLATE, NOTIFICATIONS_TEMPLATE
        
        assert "30000" in HTML_TEMPLATE  # 30s is mobile-friendly
        assert "10000" in NOTIFICATIONS_TEMPLATE  # 10s is acceptable
    
    def test_viewport_meta_tag(self):
        """Verify viewport meta tag for mobile responsiveness."""
        from src.web import HTML_TEMPLATE
        
        assert 'name="viewport"' in HTML_TEMPLATE
        assert 'content="width=device-width, initial-scale=1.0"' in HTML_TEMPLATE


class TestBackwardCompatibility:
    """Test backward compatibility with old polling approach."""
    
    def test_no_breaking_changes_to_api(self):
        """Verify REST API endpoints still work as before."""
        from src.web import create_app
        
        app = create_app(Mock(spec=HGENotifierManager))
        
        # All routes should still exist
        routes = [route.rule for route in app.url_map.iter_rules()]
        assert "/api/status" in routes
        assert "/api/refresh" in routes
        assert "/api/notifications" in routes
    
    def test_old_polling_code_removed(self):
        """Verify old unconditional polling is removed."""
        from src.web import HTML_TEMPLATE
        
        # Old code patterns that should be gone
        assert "setInterval(updateStatus, 30000)" not in HTML_TEMPLATE
        assert "setInterval(() => { if (!isConnected)" not in HTML_TEMPLATE
    
    def test_websocket_optional_not_required(self):
        """Verify app still works without WebSocket."""
        from src.web import create_app
        
        # App should initialize without WebSocketManager
        app = create_app(Mock(spec=HGENotifierManager), ws_manager=None)
        assert app is not None


class TestUserExperience:
    """Test user experience improvements."""
    
    def test_responsive_ui_with_websocket(self):
        """Verify UI is responsive when WebSocket is connected."""
        from src.web import HTML_TEMPLATE
        
        # Event listeners should be present for real-time updates
        assert "socket.on('hge_signal_update'" in HTML_TEMPLATE
        assert "socket.on('location_update'" in HTML_TEMPLATE
        assert "socket.on('distance_update'" in HTML_TEMPLATE
        assert "socket.on('status_update'" in HTML_TEMPLATE
    
    def test_graceful_degradation_without_websocket(self):
        """Verify UI degrades gracefully without WebSocket."""
        from src.web import HTML_TEMPLATE
        
        # Fallback polling mechanism should be present
        assert "pollingTimer = setInterval(updateStatusViaREST" in HTML_TEMPLATE
        assert "updateStatusViaREST()" in HTML_TEMPLATE
    
    def test_visual_connection_feedback(self):
        """Verify user gets visual feedback of connection status."""
        from src.web import HTML_TEMPLATE
        
        # Connection status indicator should be updated
        assert "updateConnectionStatus" in HTML_TEMPLATE
        assert "status-indicator" in HTML_TEMPLATE
