"""Tests for UI features: responsive design, real-time behavior, and mobile optimization.

Consolidates tests for:
- Mobile responsive enhancements (Task 9)
- UI real-time behavior optimization (Task 8)
- Touch gestures, orientation handling, and network optimizations
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from src.web import create_app, HTML_TEMPLATE, NOTIFICATIONS_TEMPLATE
from src.web.websocket import WebSocketManager
from src.core import HGENotifierManager


# ============================================================================
# MOBILE RESPONSIVE CSS TESTS
# ============================================================================


class TestMobileResponsiveCSS:
    """Test mobile-responsive CSS implementation."""
    
    def test_viewport_meta_tag_dashboard(self):
        """Verify viewport meta tag for mobile responsiveness."""
        assert 'name="viewport"' in HTML_TEMPLATE
        assert 'width=device-width' in HTML_TEMPLATE
        assert 'initial-scale=1.0' in HTML_TEMPLATE
    
    def test_viewport_meta_tag_notifications(self):
        """Verify viewport meta tag on notifications page."""
        assert 'name="viewport"' in NOTIFICATIONS_TEMPLATE
        assert 'width=device-width' in NOTIFICATIONS_TEMPLATE
    
    def test_mobile_media_query_small_screens(self):
        """Verify media query for small screens (≤600px)."""
        assert '@media (max-width: 600px)' in HTML_TEMPLATE
        assert '@media (max-width: 600px)' in NOTIFICATIONS_TEMPLATE
    
    def test_mobile_media_query_extra_small(self):
        """Verify media query for extra small screens (≤360px)."""
        assert '@media (max-width: 360px)' in HTML_TEMPLATE
        assert '@media (max-width: 360px)' in NOTIFICATIONS_TEMPLATE
    
    def test_landscape_orientation_handling(self):
        """Verify landscape orientation CSS rules."""
        assert '@media (max-width: 900px) and (orientation: landscape)' in HTML_TEMPLATE
        assert '@media (max-width: 900px) and (orientation: landscape)' in NOTIFICATIONS_TEMPLATE
    
    def test_touch_device_optimization(self):
        """Verify touch device specific CSS."""
        assert '@media (hover: none) and (pointer: coarse)' in HTML_TEMPLATE
        assert '@media (hover: none) and (pointer: coarse)' in NOTIFICATIONS_TEMPLATE
    
    def test_reduced_motion_support(self):
        """Verify accessibility for reduced motion preference."""
        assert '@media (prefers-reduced-motion: reduce)' in HTML_TEMPLATE
        assert '@media (prefers-reduced-motion: reduce)' in NOTIFICATIONS_TEMPLATE
    
    def test_dark_mode_optimization(self):
        """Verify dark mode CSS for OLED screens."""
        assert '@media (prefers-color-scheme: dark)' in HTML_TEMPLATE
    
    def test_high_dpi_support(self):
        """Verify high DPI (Retina) display support."""
        assert '(-webkit-min-device-pixel-ratio: 2)' in HTML_TEMPLATE


# ============================================================================
# TOUCH OPTIMIZATION TESTS
# ============================================================================


class TestTouchOptimization:
    """Test touch-friendly interface improvements."""
    
    def test_button_minimum_height_mobile(self):
        """Verify minimum touch target height (44px)."""
        assert 'min-height: 44px' in HTML_TEMPLATE
        assert 'min-height: 44px' in NOTIFICATIONS_TEMPLATE
    
    def test_button_padding_mobile(self):
        """Verify touch-friendly button padding."""
        # Mobile: 15px padding with 44px min-height
        assert '@media (max-width: 768px)' in HTML_TEMPLATE
        assert 'padding: 15px 20px' in HTML_TEMPLATE
    
    def test_grid_collapse_mobile(self):
        """Verify grid collapses to single column on mobile."""
        # Grid should become 1 column on small screens
        assert 'grid-template-columns: 1fr' in HTML_TEMPLATE
    
    def test_stats_grid_mobile_layout(self):
        """Verify stats grid becomes 2 columns on mobile."""
        assert 'grid-template-columns: repeat(2, 1fr)' in NOTIFICATIONS_TEMPLATE
    
    def test_font_size_adjustment_mobile(self):
        """Verify font sizes adjusted for mobile readability."""
        assert 'font-size: 14px' in HTML_TEMPLATE


# ============================================================================
# TOUCH GESTURES TESTS
# ============================================================================


class TestTouchGestures:
    """Test touch gesture support."""
    
    def test_touch_device_detection(self):
        """Verify touch device detection code exists."""
        assert 'isTouchDevice' in HTML_TEMPLATE
        assert 'ontouchstart' in HTML_TEMPLATE
        assert 'navigator.maxTouchPoints' in HTML_TEMPLATE
    
    def test_swipe_down_detection_dashboard(self):
        """Verify swipe down gesture detection on dashboard."""
        assert 'touchStartX' in HTML_TEMPLATE
        assert 'touchEndX' in HTML_TEMPLATE
        assert 'handleSwipe' in HTML_TEMPLATE
        assert 'Swipe down detected' in HTML_TEMPLATE
    
    def test_swipe_down_detection_notifications(self):
        """Verify swipe down gesture on notifications page."""
        assert 'handleSwipe' in NOTIFICATIONS_TEMPLATE
        assert 'Swipe down' in NOTIFICATIONS_TEMPLATE
    
    def test_swipe_threshold(self):
        """Verify swipe threshold is set correctly."""
        # 50px is reasonable threshold
        assert 'swipeThreshold = 50' in HTML_TEMPLATE
        assert 'swipeThreshold = 50' in NOTIFICATIONS_TEMPLATE
    
    def test_double_tap_zoom_prevention(self):
        """Verify double-tap zoom is prevented on mobile."""
        assert 'lastTouchEnd' in HTML_TEMPLATE
        assert 'lastTouchEnd <= 300' in HTML_TEMPLATE
        assert 'e.preventDefault()' in HTML_TEMPLATE


# ============================================================================
# ORIENTATION HANDLING TESTS
# ============================================================================


class TestOrientationHandling:
    """Test orientation change handling."""
    
    def test_orientation_change_listener(self):
        """Verify orientation change event listener exists."""
        assert 'orientationchange' in HTML_TEMPLATE
        assert 'orientationchange' in NOTIFICATIONS_TEMPLATE
    
    def test_orientation_detection(self):
        """Verify orientation is detected (portrait/landscape)."""
        assert 'window.innerHeight' in HTML_TEMPLATE
        assert 'window.innerWidth' in HTML_TEMPLATE
        assert 'innerHeight > innerWidth' in HTML_TEMPLATE or "innerHeight > window.innerWidth" in HTML_TEMPLATE
    
    def test_landscape_grid_adjustment(self):
        """Verify grid adjusts for landscape (2 columns)."""
        assert 'grid-template-columns: repeat(2, 1fr)' in HTML_TEMPLATE
    
    def test_landscape_console_logging(self):
        """Verify orientation changes are logged."""
        assert 'Orientation changed to' in HTML_TEMPLATE


# ============================================================================
# UI REAL-TIME BEHAVIOR TESTS
# ============================================================================


class TestUIRealtimeBehavior:
    """Test UI real-time behavior optimizations."""

    def test_polling_disabled_when_connected(self):
        """Verify polling timer is cleared when WebSocket connects."""
        assert "pollingTimer = null" in HTML_TEMPLATE
        assert "clearInterval(pollingTimer)" in HTML_TEMPLATE
        assert "Polling stopped - using real-time updates" in HTML_TEMPLATE
    
    def test_polling_enabled_when_disconnected(self):
        """Verify polling timer is started when WebSocket disconnects."""
        assert "pollingTimer = setInterval(updateStatusViaREST" in HTML_TEMPLATE
        assert "Starting fallback polling" in HTML_TEMPLATE
        assert "POLLING_INTERVAL_MS = 30000" in HTML_TEMPLATE
    
    def test_polling_interval_dashboard(self):
        """Verify dashboard polling interval is 30 seconds."""
        # Dashboard should use 30s polling
        assert "POLLING_INTERVAL_MS = 30000" in HTML_TEMPLATE
        assert "30 seconds fallback polling" in HTML_TEMPLATE
    
    def test_polling_interval_notifications(self):
        """Verify notifications polling interval is 10 seconds."""
        # Notifications should use 10s polling
        assert "NOTIFICATIONS_POLLING_INTERVAL_MS = 10000" in NOTIFICATIONS_TEMPLATE
        assert "10 seconds fallback polling" in NOTIFICATIONS_TEMPLATE
    
    def test_immediate_refresh_on_disconnect(self):
        """Verify immediate data refresh on disconnect before polling starts."""
        # Should immediately call updateStatusViaREST without waiting for interval
        assert "updateStatusViaREST()" in HTML_TEMPLATE
        assert "Immediate refresh to avoid waiting for first interval" in HTML_TEMPLATE
    
    def test_rest_update_function_exists(self):
        """Verify REST API update function is defined."""
        assert "function updateStatusViaREST()" in HTML_TEMPLATE
        assert "fetch(statusEndpoint)" in HTML_TEMPLATE
        assert "renderStatus(data)" in HTML_TEMPLATE


# ============================================================================
# DASHBOARD REAL-TIME TESTS
# ============================================================================


class TestDashboardRealtime:
    """Test dashboard real-time update behavior."""
    
    def test_websocket_event_listeners(self):
        """Verify dashboard has all WebSocket event listeners."""
        # Check for all 4 channel listeners
        assert "socket.on('hge_signal_update'" in HTML_TEMPLATE
        assert "socket.on('location_update'" in HTML_TEMPLATE
        assert "socket.on('distance_update'" in HTML_TEMPLATE
        assert "socket.on('status_update'" in HTML_TEMPLATE
    
    def test_initial_load_via_rest(self):
        """Verify initial load uses REST API, not polling."""
        # Should call updateStatusViaREST on initial load
        assert "updateStatusViaREST();" in HTML_TEMPLATE
        # Should NOT have old polling setup
        assert "setInterval(updateStatus, 30000)" not in HTML_TEMPLATE
    
    def test_refresh_button_works_regardless_of_connection(self):
        """Verify refresh button works with both WebSocket and REST."""
        # Refresh should always work
        assert "function refreshStatus()" in HTML_TEMPLATE
        assert "fetch(refreshEndpoint" in HTML_TEMPLATE
        assert "renderStatus(data.data)" in HTML_TEMPLATE
    
    def test_connection_status_indicator(self):
        """Verify connection status indicator updates."""
        assert "updateConnectionStatus(true)" in HTML_TEMPLATE
        assert "updateConnectionStatus(false)" in HTML_TEMPLATE
        assert "status-indicator" in HTML_TEMPLATE


# ============================================================================
# NOTIFICATIONS REAL-TIME TESTS
# ============================================================================


class TestNotificationsRealtime:
    """Test notifications page real-time update behavior."""
    
    def test_notifications_polling_timer_management(self):
        """Verify notifications polling timer is properly managed."""
        assert "notificationsPollingTimer = null" in NOTIFICATIONS_TEMPLATE
        assert "clearInterval(notificationsPollingTimer)" in NOTIFICATIONS_TEMPLATE
        assert "notificationsPollingTimer = setInterval(loadNotifications" in NOTIFICATIONS_TEMPLATE
    
    def test_notifications_immediate_load_on_disconnect(self):
        """Verify notifications immediately load on disconnect."""
        # Should immediately call loadNotifications without waiting
        assert "loadNotifications();" in NOTIFICATIONS_TEMPLATE
    
    def test_notifications_status_channel_subscription(self):
        """Verify notifications subscribe to status channel only."""
        assert "channels: ['status']" in NOTIFICATIONS_TEMPLATE
        # Should listen for status updates
        assert "socket.on('status_update'" in NOTIFICATIONS_TEMPLATE


# ============================================================================
# POLLING FALLBACK TESTS
# ============================================================================


class TestPollingFallback:
    """Test fallback polling behavior when WebSocket is unavailable."""
    
    def test_rest_api_fallback_error_handling(self):
        """Verify REST API fallback handles errors gracefully."""
        # Should have error handling
        assert ".catch(error =>" in HTML_TEMPLATE
        assert "Error fetching status via REST" in HTML_TEMPLATE
    
    def test_rest_api_checks_response_status(self):
        """Verify REST API fallback checks HTTP status."""
        assert "if (!response.ok)" in HTML_TEMPLATE

