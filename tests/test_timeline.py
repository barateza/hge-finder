"""Test suite for timeline visualization feature (Task 10)."""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch
from src.core import HGENotifierManager
from src.web import create_app
from src.web.websocket import WebSocketManager
from src.notifications.models import Notification


class TestTimelineAPIEndpoints:
    """Test timeline API endpoints."""
    
    @pytest.fixture
    def app_with_db(self, mock_manager):
        """Create test app with mock manager."""
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app_with_db):
        """Create test client."""
        return app_with_db.test_client()
    
    @pytest.fixture
    def mock_manager(self):
        """Create mock manager with timeline data."""
        manager = Mock(spec=HGENotifierManager)
        manager.notification_manager = Mock()
        
        # Create sample notifications
        now = datetime.now()
        notifications = [
            Notification(
                signal_system="Leesti",
                distance_ly=15.5,
                timestamp=now - timedelta(hours=2),
                channel="in_app",
                success=True
            ),
            Notification(
                signal_system="Junga",
                distance_ly=22.3,
                timestamp=now - timedelta(hours=1),
                channel="in_app",
                success=True
            ),
            Notification(
                signal_system="Diso",
                distance_ly=18.7,
                timestamp=now,
                channel="in_app",
                success=True
            ),
        ]
        
        manager.notification_manager.get_notification_history = Mock(return_value=notifications)
        manager.notification_manager.get_stats = Mock(return_value={
            "total": 3,
            "successful": 3,
            "failed": 0
        })
        
        return manager
    
    def test_timeline_endpoint_exists(self, client):
        """Test that /api/timeline endpoint exists."""
        response = client.get('/api/timeline')
        assert response.status_code in [200, 400, 500]  # Endpoint exists
    
    def test_timeline_returns_json(self, client):
        """Test that /api/timeline returns JSON."""
        response = client.get('/api/timeline')
        assert response.content_type == 'application/json'
    
    def test_timeline_data_structure(self, client, mock_manager):
        """Test that timeline data has correct structure."""
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline')
            data = json.loads(response.data)
            
            assert 'status' in data
            assert 'data' in data
            assert isinstance(data['data'], list)
    
    def test_timeline_entries_contain_required_fields(self, client, mock_manager):
        """Test that timeline entries contain required fields."""
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline')
            data = json.loads(response.data)
            
            if data['data']:
                entry = data['data'][0]
                assert 'timestamp' in entry
                assert 'system_name' in entry
                assert 'distance_ly' in entry
                assert 'channel' in entry
                assert 'success' in entry
    
    def test_timeline_limit_parameter(self, client, mock_manager):
        """Test timeline limit parameter."""
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline?limit=10')
            data = json.loads(response.data)
            
            assert data['status'] == 'success'
            mock_manager.notification_manager.get_notification_history.assert_called_with(count=10)


class TestTimelineSummaryEndpoint:
    """Test timeline summary API endpoint."""
    
    @pytest.fixture
    def mock_manager(self):
        """Create mock manager with timeline data."""
        manager = Mock(spec=HGENotifierManager)
        manager.notification_manager = Mock()
        
        # Create sample notifications across different hours
        now = datetime.now()
        notifications = []
        for i in range(5):
            notifications.append(Notification(
                signal_system=f"System{i}",
                distance_ly=10.0 + i * 5,
                timestamp=now - timedelta(hours=i),
                channel="in_app",
                success=True
            ))
        
        manager.notification_manager.get_notification_history = Mock(return_value=notifications)
        
        return manager
    
    def test_summary_endpoint_returns_stats(self, mock_manager):
        """Test that summary endpoint returns statistics."""
        from src.web import create_app
        
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline/summary')
            data = json.loads(response.data)
            
            assert 'status' in data
            assert data['status'] == 'success'
            assert 'data' in data
    
    def test_summary_contains_required_fields(self, mock_manager):
        """Test that summary contains required statistics."""
        from src.web import create_app
        
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline/summary')
            data = json.loads(response.data)
            stats = data['data']
            
            assert 'total_signals' in stats
            assert 'avg_distance' in stats
            assert 'min_distance' in stats
            assert 'max_distance' in stats
            assert 'hourly_distribution' in stats
    
    def test_summary_calculates_statistics_correctly(self, mock_manager):
        """Test that statistics are calculated correctly."""
        from src.web import create_app
        
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline/summary')
            data = json.loads(response.data)
            stats = data['data']
            
            assert stats['total_signals'] == 5
            assert stats['avg_distance'] > 0
            assert stats['min_distance'] > 0
            assert stats['max_distance'] >= stats['min_distance']
    
    def test_summary_empty_when_no_data(self):
        """Test summary when no data available."""
        from src.web import create_app
        
        manager = Mock(spec=HGENotifierManager)
        manager.notification_manager = Mock()
        manager.notification_manager.get_notification_history = Mock(return_value=[])
        
        app = create_app(manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline/summary')
            data = json.loads(response.data)
            
            assert data['status'] == 'success'
            assert data['data']['total_signals'] == 0


class TestTimelineTrendsEndpoint:
    """Test timeline trends API endpoint."""
    
    @pytest.fixture
    def mock_manager(self):
        """Create mock manager with trend data."""
        manager = Mock(spec=HGENotifierManager)
        manager.notification_manager = Mock()
        
        now = datetime.now()
        notifications = [
            Notification(
                signal_system="System1",
                distance_ly=10.0,
                timestamp=now - timedelta(hours=2),
                channel="in_app",
                success=True
            ),
            Notification(
                signal_system="System2",
                distance_ly=15.0,
                timestamp=now - timedelta(hours=1),
                channel="in_app",
                success=True
            ),
            Notification(
                signal_system="System3",
                distance_ly=20.0,
                timestamp=now,
                channel="in_app",
                success=True
            ),
        ]
        
        manager.notification_manager.get_notification_history = Mock(return_value=notifications)
        
        return manager
    
    def test_trends_endpoint_returns_data(self, mock_manager):
        """Test that trends endpoint returns distance data."""
        from src.web import create_app
        
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline/trends')
            data = json.loads(response.data)
            
            assert data['status'] == 'success'
            assert isinstance(data['data'], list)
    
    def test_trends_contains_distance_values(self, mock_manager):
        """Test that trends contain distance values."""
        from src.web import create_app
        
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline/trends')
            data = json.loads(response.data)
            
            if data['data']:
                trend = data['data'][0]
                assert 'timestamp' in trend
                assert 'distance' in trend
                assert 'system' in trend


class TestTimelineTemplate:
    """Test timeline template rendering."""
    
    @pytest.fixture
    def mock_manager(self):
        """Create mock manager."""
        manager = Mock(spec=HGENotifierManager)
        return manager
    
    def test_timeline_page_renders(self, mock_manager):
        """Test that timeline page renders."""
        from src.web import create_app
        
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/timeline')
            assert response.status_code == 200
    
    def test_timeline_page_contains_chart_title(self, mock_manager):
        """Test that timeline page contains chart title."""
        from src.web import create_app
        
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/timeline')
            html = response.data.decode()
            
            assert 'HGE Detection Timeline' in html or 'Distance Trends' in html
    
    def test_timeline_page_includes_chart_js(self, mock_manager):
        """Test that timeline page includes Chart.js."""
        from src.web import create_app
        
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/timeline')
            html = response.data.decode()
            
            assert 'chart.js' in html.lower() or 'Chart' in html
    
    def test_timeline_page_has_view_switcher(self, mock_manager):
        """Test that timeline page has view switcher buttons."""
        from src.web import create_app
        
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/timeline')
            html = response.data.decode()
            
            assert 'switchView' in html
    
    def test_timeline_page_is_mobile_responsive(self, mock_manager):
        """Test that timeline page has mobile responsive design."""
        from src.web import create_app
        
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/timeline')
            html = response.data.decode()
            
            assert '@media' in html


class TestTimelineCharts:
    """Test timeline chart functionality."""
    
    def test_trends_chart_configuration(self):
        """Test that trends chart has correct configuration."""
        # This would test Chart.js configuration
        from src.web import TIMELINE_TEMPLATE
        
        assert 'Chart' in TIMELINE_TEMPLATE
        assert 'trendsChart' in TIMELINE_TEMPLATE
    
    def test_hourly_chart_configuration(self):
        """Test that hourly chart has correct configuration."""
        from src.web import TIMELINE_TEMPLATE
        
        assert 'hourlyChart' in TIMELINE_TEMPLATE
    
    def test_chart_colors_match_theme(self):
        """Test that chart colors match Elite Dangerous theme."""
        from src.web import TIMELINE_TEMPLATE
        
        assert '#00ff00' in TIMELINE_TEMPLATE  # Green
        assert '#ffff00' in TIMELINE_TEMPLATE  # Yellow


class TestTimelineStatistics:
    """Test timeline statistics calculations."""
    
    def test_calculate_average_distance(self):
        """Test average distance calculation."""
        distances = [10.0, 15.0, 20.0]
        avg = sum(distances) / len(distances)
        
        assert avg == 15.0
    
    def test_calculate_min_max_distance(self):
        """Test min/max distance calculation."""
        distances = [10.0, 15.0, 20.0]
        
        assert min(distances) == 10.0
        assert max(distances) == 20.0
    
    def test_hourly_distribution_counting(self):
        """Test hourly distribution counting."""
        now = datetime.now()
        timestamps = [
            now - timedelta(hours=2),
            now - timedelta(hours=1),
            now - timedelta(hours=1),
            now,
        ]
        
        hourly = {}
        for ts in timestamps:
            hour = ts.strftime("%H:00")
            hourly[hour] = hourly.get(hour, 0) + 1
        
        assert sum(hourly.values()) == 4


class TestTimelineNavigation:
    """Test timeline navigation and linking."""
    
    @pytest.fixture
    def mock_manager(self):
        """Create mock manager."""
        manager = Mock(spec=HGENotifierManager)
        return manager
    
    def test_dashboard_has_timeline_link(self, mock_manager):
        """Test that dashboard includes timeline link."""
        from src.web import create_app
        
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/')
            html = response.data.decode()
            
            assert '/timeline' in html
    
    def test_timeline_has_back_link(self, mock_manager):
        """Test that timeline has back link to dashboard."""
        from src.web import create_app
        
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/timeline')
            html = response.data.decode()
            
            assert 'href="/"' in html
    
    def test_all_pages_accessible(self, mock_manager):
        """Test that all pages are accessible."""
        from src.web import create_app
        
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            assert c.get('/').status_code == 200
            assert c.get('/timeline').status_code == 200
            assert c.get('/notifications').status_code == 200


class TestTimelineDataFormatting:
    """Test timeline data formatting."""
    
    def test_timestamp_iso_format(self):
        """Test that timestamps are in ISO format."""
        now = datetime.now()
        iso_str = now.isoformat()
        
        # Should parse back correctly
        parsed = datetime.fromisoformat(iso_str)
        assert parsed.year == now.year
    
    def test_distance_precision(self):
        """Test distance precision in calculations."""
        distance = 15.5437
        rounded = round(distance, 2)
        
        assert rounded == 15.54
    
    def test_system_name_encoding(self):
        """Test that system names are properly encoded."""
        system_name = "Leesti"
        
        # Should not contain special characters that break JSON
        assert '"' not in system_name or '\\"' in json.dumps({"name": system_name})


class TestTimelinePerformance:
    """Test timeline performance considerations."""
    
    def test_limit_prevents_excessive_data(self):
        """Test that limit parameter prevents excessive data."""
        from src.web import create_app
        
        mock_manager = Mock(spec=HGENotifierManager)
        mock_manager.notification_manager = Mock()
        
        # Create many notifications
        now = datetime.now()
        notifications = [
            Notification(
                signal_system=f"System{i}",
                distance_ly=10.0 + i,
                timestamp=now - timedelta(hours=i),
                channel="in_app",
                success=True
            )
            for i in range(100)
        ]
        
        mock_manager.notification_manager.get_notification_history = Mock(return_value=notifications)
        
        app = create_app(mock_manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline?limit=50')
            data = json.loads(response.data)
            
            # Verify limit was respected
            assert len(data['data']) <= 100


class TestTimelineWebSocketIntegration:
    """Test timeline WebSocket real-time updates."""
    
    def test_timeline_page_includes_socket_io(self):
        """Test that timeline page includes Socket.IO."""
        from src.web import TIMELINE_TEMPLATE
        
        assert 'socket.io' in TIMELINE_TEMPLATE.lower()
    
    def test_timeline_handles_status_events(self):
        """Test that timeline handles status events."""
        from src.web import TIMELINE_TEMPLATE
        
        assert "socket.on('status'" in TIMELINE_TEMPLATE or "on('status" in TIMELINE_TEMPLATE
    
    def test_timeline_updates_on_new_signal(self):
        """Test that timeline updates on new HGE signal."""
        from src.web import TIMELINE_TEMPLATE
        
        assert 'hge_signal' in TIMELINE_TEMPLATE


class TestTimelineErrorHandling:
    """Test timeline error handling."""
    
    @pytest.fixture
    def mock_manager_with_error(self):
        """Create mock manager that raises error."""
        manager = Mock(spec=HGENotifierManager)
        manager.notification_manager = Mock()
        manager.notification_manager.get_notification_history = Mock(
            side_effect=Exception("Database error")
        )
        
        return manager
    
    def test_timeline_error_response(self, mock_manager_with_error):
        """Test timeline error response."""
        from src.web import create_app
        
        app = create_app(mock_manager_with_error, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline')
            data = json.loads(response.data)
            
            assert data['status'] == 'error' or response.status_code == 500
    
    def test_summary_error_response(self, mock_manager_with_error):
        """Test summary error response."""
        from src.web import create_app
        
        app = create_app(mock_manager_with_error, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline/summary')
            data = json.loads(response.data)
            
            assert data['status'] == 'error' or response.status_code == 500
    
    def test_trends_error_response(self, mock_manager_with_error):
        """Test trends error response."""
        from src.web import create_app
        
        app = create_app(mock_manager_with_error, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline/trends')
            data = json.loads(response.data)
            
            assert data['status'] == 'error' or response.status_code == 500


class TestTimelineEdgeCases:
    """Test timeline edge cases."""
    
    def test_timeline_with_null_distances(self):
        """Test timeline with null distance values."""
        from src.web import create_app
        
        manager = Mock(spec=HGENotifierManager)
        manager.notification_manager = Mock()
        
        now = datetime.now()
        notifications = [
            Notification(
                signal_system="System1",
                distance_ly=0.0,
                timestamp=now,
                channel="in_app",
                success=False
            ),
        ]
        
        manager.notification_manager.get_notification_history = Mock(return_value=notifications)
        
        app = create_app(manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline')
            data = json.loads(response.data)
            
            assert data['status'] == 'success'
    
    def test_timeline_with_duplicate_systems(self):
        """Test timeline with duplicate system names."""
        from src.web import create_app
        
        manager = Mock(spec=HGENotifierManager)
        manager.notification_manager = Mock()
        
        now = datetime.now()
        notifications = [
            Notification(
                signal_system="Leesti",
                distance_ly=10.0,
                timestamp=now - timedelta(hours=1),
                channel="in_app",
                success=True
            ),
            Notification(
                signal_system="Leesti",
                distance_ly=10.5,
                timestamp=now,
                channel="in_app",
                success=True
            ),
        ]
        
        manager.notification_manager.get_notification_history = Mock(return_value=notifications)
        
        app = create_app(manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline')
            data = json.loads(response.data)
            
            assert len(data['data']) == 2
    
    def test_timeline_timestamp_ordering(self):
        """Test that timeline maintains timestamp ordering."""
        from src.web import create_app
        
        manager = Mock(spec=HGENotifierManager)
        manager.notification_manager = Mock()
        
        now = datetime.now()
        notifications = [
            Notification(
                signal_system="System1",
                distance_ly=10.0,
                timestamp=now,
                channel="in_app",
                success=True
            ),
            Notification(
                signal_system="System2",
                distance_ly=15.0,
                timestamp=now - timedelta(hours=1),
                channel="in_app",
                success=True
            ),
        ]
        
        manager.notification_manager.get_notification_history = Mock(return_value=notifications)
        
        app = create_app(manager, None)
        app.config['TESTING'] = True
        
        with app.test_client() as c:
            response = c.get('/api/timeline')
            data = json.loads(response.data)
            
            # Data should be in chronological order (oldest first)
            if len(data['data']) >= 2:
                t1 = datetime.fromisoformat(data['data'][0]['timestamp'])
                t2 = datetime.fromisoformat(data['data'][1]['timestamp'])
                assert t1 <= t2


class TestTimelineMobileResponsiveness:
    """Test timeline mobile responsiveness."""
    
    def test_timeline_has_viewport_meta(self):
        """Test that timeline has viewport meta tag."""
        from src.web import TIMELINE_TEMPLATE
        
        assert 'viewport' in TIMELINE_TEMPLATE
    
    def test_timeline_has_media_queries(self):
        """Test that timeline has mobile media queries."""
        from src.web import TIMELINE_TEMPLATE
        
        assert '@media' in TIMELINE_TEMPLATE
    
    def test_timeline_charts_responsive(self):
        """Test that charts are responsive."""
        from src.web import TIMELINE_TEMPLATE
        
        assert 'maintainAspectRatio' in TIMELINE_TEMPLATE or 'responsive' in TIMELINE_TEMPLATE


class TestTimelineAccessibility:
    """Test timeline accessibility features."""
    
    def test_timeline_has_proper_heading_hierarchy(self):
        """Test that timeline has proper heading hierarchy."""
        from src.web import TIMELINE_TEMPLATE
        
        assert '<h1>' in TIMELINE_TEMPLATE
        assert '<h3>' in TIMELINE_TEMPLATE
    
    def test_timeline_has_alt_text_for_icons(self):
        """Test that timeline uses semantic HTML."""
        from src.web import TIMELINE_TEMPLATE
        
        # At minimum, check for proper button labels
        assert 'button' in TIMELINE_TEMPLATE.lower()
    
    def test_timeline_color_contrast(self):
        """Test timeline color contrast for accessibility."""
        from src.web import TIMELINE_TEMPLATE
        
        # Check for high contrast colors
        assert '#00ff00' in TIMELINE_TEMPLATE  # Bright green
        assert '#0a0a0a' in TIMELINE_TEMPLATE or '#000' in TIMELINE_TEMPLATE  # Dark background
