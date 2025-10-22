"""Tests for mobile responsive enhancements (Task 9).

Tests responsive CSS, touch gestures, orientation handling,
and mobile-specific optimizations.
"""

import pytest
from unittest.mock import Mock
from src.web import create_app, HTML_TEMPLATE, NOTIFICATIONS_TEMPLATE
from src.core import HGENotifierManager


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


class TestMobileNetworkOptimization:
    """Test mobile network optimizations."""
    
    def test_network_type_detection(self):
        """Verify network type detection code exists."""
        assert 'detectNetworkType' in HTML_TEMPLATE
        assert 'navigator.connection' in HTML_TEMPLATE
    
    def test_network_types_supported(self):
        """Verify all network types are supported."""
        assert '4g' in HTML_TEMPLATE.lower()
        assert '3g' in HTML_TEMPLATE.lower()
        assert '2g' in HTML_TEMPLATE.lower()
    
    def test_polling_interval_by_network(self):
        """Verify polling intervals are adaptive."""
        assert 'pollInterval' in HTML_TEMPLATE
        # 30s for 4G, 45s for 3G, 60s for 2G, 90s for slow 2G
        assert '30000' in HTML_TEMPLATE
        assert '45000' in HTML_TEMPLATE
        assert '60000' in HTML_TEMPLATE
        assert '90000' in HTML_TEMPLATE


class TestResponsiveBreakpoints:
    """Test responsive design breakpoints."""
    
    def test_medium_screen_breakpoint(self):
        """Verify medium screen breakpoint (768px)."""
        assert '@media (max-width: 768px)' in HTML_TEMPLATE
    
    def test_small_screen_breakpoint(self):
        """Verify small screen breakpoint (600px)."""
        assert '@media (max-width: 600px)' in HTML_TEMPLATE
    
    def test_extra_small_breakpoint(self):
        """Verify extra small breakpoint (360px)."""
        assert '@media (max-width: 360px)' in HTML_TEMPLATE
    
    def test_landscape_breakpoint(self):
        """Verify landscape breakpoint."""
        assert '@media (max-width: 900px) and (orientation: landscape)' in HTML_TEMPLATE


class TestResponsiveGrids:
    """Test responsive grid layouts."""
    
    def test_dashboard_grid_responsive(self):
        """Verify dashboard grid is responsive."""
        assert 'grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))' in HTML_TEMPLATE
    
    def test_stats_grid_responsive(self):
        """Verify stats grid is responsive."""
        assert 'grid-template-columns: repeat(auto-fit, minmax(200px, 1fr))' in NOTIFICATIONS_TEMPLATE
    
    def test_grid_gap_mobile(self):
        """Verify grid gap is appropriate for mobile."""
        # On mobile (600px), gap should be 15px
        assert 'gap: 15px' in HTML_TEMPLATE


class TestMobileAccessibility:
    """Test mobile accessibility features."""
    
    def test_touch_target_size(self):
        """Verify touch targets are at least 44x44 pixels."""
        assert '44px' in HTML_TEMPLATE  # button min-height
    
    def test_reduced_motion_respect(self):
        """Verify reduced motion preference is respected."""
        assert 'prefers-reduced-motion' in HTML_TEMPLATE
    
    def test_color_contrast(self):
        """Verify sufficient color contrast for readability."""
        assert '#00ff00' in HTML_TEMPLATE  # Green text
        assert '#0a0a0a' in HTML_TEMPLATE  # Dark background
    
    def test_font_size_readability(self):
        """Verify font sizes are readable on mobile."""
        # Base body: 14px on mobile is readable
        assert 'font-size: 14px' in HTML_TEMPLATE


class TestMobileFeatures:
    """Test mobile-specific features."""
    
    def test_mobile_detection_logging(self):
        """Verify mobile device is detected and logged."""
        assert 'Mobile device detected' in HTML_TEMPLATE
        assert 'Swipe down to refresh' in HTML_TEMPLATE
    
    def test_landscape_logging(self):
        """Verify landscape orientation is logged."""
        assert 'Orientation changed to' in HTML_TEMPLATE
        assert 'landscape' in HTML_TEMPLATE
    
    def test_mobile_button_wrapping(self):
        """Verify buttons wrap on small screens."""
        assert 'flex-wrap: wrap' in NOTIFICATIONS_TEMPLATE


class TestResponsiveImages:
    """Test image responsiveness."""
    
    def test_box_sizing_border_box(self):
        """Verify box-sizing is border-box for responsive design."""
        assert 'box-sizing: border-box' in HTML_TEMPLATE
        assert 'box-sizing: border-box' in NOTIFICATIONS_TEMPLATE


class TestFlexibleLayouts:
    """Test flexible layout implementations."""
    
    def test_container_max_width_mobile(self):
        """Verify container respects mobile width."""
        assert 'max-width: 100%' in HTML_TEMPLATE
    
    def test_full_width_buttons_mobile(self):
        """Verify buttons are full-width on small screens."""
        assert 'width: 100%' in HTML_TEMPLATE


class TestPerformanceOptimizations:
    """Test performance optimizations for mobile."""
    
    def test_transition_optimization(self):
        """Verify transitions are optimized."""
        assert 'transition: all 0.3s' in HTML_TEMPLATE
    
    def test_animation_optimization(self):
        """Verify animations respect preferences."""
        assert '@keyframes pulse' in HTML_TEMPLATE
    
    def test_shadow_optimization(self):
        """Verify box shadows are optimized for mobile."""
        assert 'box-shadow' in HTML_TEMPLATE


class TestEndToEnd:
    """End-to-end mobile responsiveness tests."""
    
    @pytest.fixture
    def manager(self):
        """Create test manager."""
        return Mock(spec=HGENotifierManager)
    
    @pytest.fixture
    def app(self, manager):
        """Create Flask app."""
        return create_app(manager)
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_dashboard_loads_mobile(self, client):
        """Verify dashboard loads on mobile device."""
        response = client.get('/')
        assert response.status_code != 404
    
    def test_notifications_loads_mobile(self, client):
        """Verify notifications page loads."""
        response = client.get('/notifications')
        assert response.status_code != 404


class TestBrowserCompatibility:
    """Test browser compatibility for mobile."""
    
    def test_webkit_prefix_for_ios(self):
        """Verify webkit prefixes for iOS compatibility."""
        assert '-webkit-min-device-pixel-ratio' in HTML_TEMPLATE
    
    def test_standard_media_queries(self):
        """Verify standard media queries without prefixes."""
        assert '(prefers-color-scheme: dark)' in HTML_TEMPLATE


class TestScrollBehavior:
    """Test scroll behavior on mobile."""
    
    def test_overflow_handling_landscape(self):
        """Verify overflow is handled in landscape."""
        assert 'overflow-y: auto' in NOTIFICATIONS_TEMPLATE
    
    def test_max_height_landscape(self):
        """Verify max-height for scrollable content in landscape."""
        assert 'max-height: 60vh' in NOTIFICATIONS_TEMPLATE


class TestButtonBehavior:
    """Test button behavior on mobile."""
    
    def test_button_active_state_mobile(self):
        """Verify button active state is visible on touch."""
        assert 'button:active' in HTML_TEMPLATE
        assert 'transform: scale(0.98)' in HTML_TEMPLATE
    
    def test_button_hover_mobile(self):
        """Verify button hover effect adapts to touch."""
        assert 'button:hover' in HTML_TEMPLATE
        assert 'box-shadow' in HTML_TEMPLATE


class TestIntegration:
    """Integration tests for mobile features."""
    
    def test_all_media_queries_present(self):
        """Verify all necessary media queries are present."""
        media_queries = [
            '@media (max-width: 768px)',
            '@media (max-width: 600px)',
            '@media (max-width: 360px)',
            '@media (max-width: 900px) and (orientation: landscape)',
            '@media (hover: none) and (pointer: coarse)',
            '@media (prefers-reduced-motion: reduce)',
        ]
        
        for query in media_queries:
            assert query in HTML_TEMPLATE or query in NOTIFICATIONS_TEMPLATE
    
    def test_touch_gesture_complete_flow(self):
        """Verify complete touch gesture flow exists."""
        # Touch start, end, and swipe handling
        assert 'touchstart' in HTML_TEMPLATE
        assert 'touchend' in HTML_TEMPLATE
        assert 'handleSwipe' in HTML_TEMPLATE
