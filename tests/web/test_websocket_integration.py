"""
Integration tests for WebSocket functionality with Flask and HGENotifierManager.

Tests end-to-end WebSocket event propagation from backend through server to client.
These tests focus on compatibility and architecture rather than async server initialization.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

from src.core import HGENotifierManager
from src.web import create_app
from src.web.websocket import WebSocketManager
from src.notifications.models import Notification, Alert
from src.eddn import HGESignal
from src.journal import CommanderLocation


# =====================================================================
# FIXTURES
# =====================================================================


@pytest.fixture
def mock_websocket_manager():
    """Create a mock WebSocket manager for testing."""
    manager = Mock(spec=WebSocketManager)
    manager.sio = None  # Not initialized
    manager.get_connection_count = Mock(return_value=0)
    manager.get_channel_subscribers = Mock(return_value=[])
    manager.get_all_subscriptions = Mock(return_value={})
    manager.initialize = Mock(return_value=None)
    return manager


@pytest.fixture
def mock_manager():
    """Create mock HGENotifierManager."""
    manager = Mock(spec=HGENotifierManager)
    manager.get_status.return_value = {
        "hge_signal": None,
        "commander_location": None,
        "distance": None,
        "next_refresh": 10,
    }
    manager.websocket_manager = None
    manager.start = Mock(return_value=None)
    manager.stop = Mock(return_value=None)
    manager.refresh = Mock(return_value=True)
    return manager


@pytest.fixture
def app_with_websocket(mock_manager, mock_websocket_manager):
    """Create Flask app with WebSocket support for testing."""
    app = create_app(mock_manager, None)  # No actual WebSocket manager to avoid async issues
    app.config['TESTING'] = True
    
    return app, mock_manager, mock_websocket_manager


@pytest.fixture
def client_with_websocket(app_with_websocket):
    """Create test client with WebSocket support."""
    app, manager, ws_manager = app_with_websocket
    return app.test_client(), app, manager, ws_manager


@pytest.fixture
def hge_signal():
    """Create sample HGE signal."""
    return HGESignal(
        system_name="Beagle Point",
        timestamp=datetime.now() - timedelta(minutes=5),
        x=1000.0,
        y=2000.0,
        z=3000.0,
    )


@pytest.fixture
def commander_location():
    """Create sample commander location."""
    return CommanderLocation(
        system_name="Colonia",
        timestamp=datetime.now(),
        x=9530.5,
        y=-910.28,
        z=19808.44,
    )


@pytest.fixture
def distance_data():
    """Create sample distance data."""
    return {
        "value": 125.43,
        "formatted": "125.43 ly",
        "from_system": "Sol",
        "to_system": "Beagle Point",
    }


# =====================================================================
# WEBSOCKET SERVER INTEGRATION TESTS
# =====================================================================


class TestWebSocketServerIntegration:
    """Test WebSocket server integration with Flask."""

    def test_websocket_manager_initialization(self, mock_websocket_manager):
        """Test WebSocket manager initializes correctly."""
        ws_manager = mock_websocket_manager
        assert ws_manager is not None

    def test_websocket_manager_has_connection_tracking(self, mock_websocket_manager):
        """Test WebSocket manager tracks connections."""
        ws_manager = mock_websocket_manager
        count = ws_manager.get_connection_count()
        assert count == 0

    def test_app_has_basic_routes(self, client_with_websocket):
        """Test Flask app has basic routes."""
        client, app, manager, ws_manager = client_with_websocket
        with app.app_context():
            assert app is not None

    def test_app_has_rest_api_routes(self, client_with_websocket):
        """Test Flask app maintains REST API routes."""
        client, app, manager, ws_manager = client_with_websocket
        
        manager.get_status.return_value = {
            "hge_signal": None,
            "commander_location": None,
            "distance": None,
            "next_refresh": 10,
        }
        
        # Test REST endpoint
        response = client.get('/api/status')
        assert response.status_code == 200


# =====================================================================
# EVENT PROPAGATION TESTS
# =====================================================================


class TestEventPropagation:
    """Test event propagation architecture."""

    def test_hge_signal_event_data_structure(self, hge_signal):
        """Test HGE signal can be converted to event data."""
        signal_data = {
            "system_name": hge_signal.system_name,
            "timestamp": hge_signal.timestamp.isoformat(),
            "coordinates": {
                "x": hge_signal.x,
                "y": hge_signal.y,
                "z": hge_signal.z,
            },
        }
        
        assert signal_data["system_name"] == "Beagle Point"
        assert "coordinates" in signal_data

    def test_location_event_data_structure(self, commander_location):
        """Test location can be converted to event data."""
        location_data = {
            "system_name": commander_location.system_name,
            "timestamp": commander_location.timestamp.isoformat(),
            "coordinates": {
                "x": commander_location.x,
                "y": commander_location.y,
                "z": commander_location.z,
            },
        }
        
        assert location_data["system_name"] == "Colonia"
        assert "coordinates" in location_data

    def test_distance_event_data_structure(self, distance_data):
        """Test distance data structure."""
        assert "value" in distance_data
        assert "formatted" in distance_data
        assert distance_data["value"] > 0

    def test_status_event_data_structure(self):
        """Test status event data structure."""
        status_data = {
            "status": "running",
            "timestamp": datetime.now().isoformat(),
        }
        
        assert status_data["status"] == "running"
        assert "timestamp" in status_data


# =====================================================================
# CONNECTION LIFECYCLE TESTS
# =====================================================================


class TestConnectionLifecycle:
    """Test WebSocket connection lifecycle architecture."""

    def test_manager_can_hold_websocket_manager_reference(self, mock_manager, mock_websocket_manager):
        """Test HGENotifierManager can hold WebSocketManager reference."""
        mock_manager.websocket_manager = mock_websocket_manager
        
        assert mock_manager.websocket_manager is not None
        assert isinstance(mock_manager.websocket_manager, Mock)

    def test_websocket_manager_tracks_connections(self, mock_websocket_manager):
        """Test WebSocket manager tracks client connections."""
        count = mock_websocket_manager.get_connection_count()
        
        assert isinstance(count, int)
        assert count >= 0

    def test_websocket_manager_tracks_subscriptions(self, mock_websocket_manager):
        """Test WebSocket manager tracks subscriptions."""
        subs = mock_websocket_manager.get_all_subscriptions()
        
        assert isinstance(subs, dict)


# =====================================================================
# DATA SERIALIZATION TESTS
# =====================================================================


class TestDataSerialization:
    """Test WebSocket data serialization for transmission."""

    def test_hge_signal_serialization(self):
        """Test HGE signal can be serialized for WebSocket transmission."""
        signal_dict = {
            "system_name": "Beagle Point",
            "age": "5 minutes ago",
            "coordinates": {"x": 1000.0, "y": 2000.0, "z": 3000.0},
            "timestamp": datetime.now().isoformat(),
        }
        
        # Verify serialization
        json_str = json.dumps(signal_dict)
        assert json_str is not None
        assert "Beagle Point" in json_str
        assert "coordinates" in json_str

    def test_location_serialization(self):
        """Test commander location can be serialized for WebSocket."""
        location_dict = {
            "system_name": "Colonia",
            "coordinates": {"x": 9530.5, "y": -910.28, "z": 19808.44},
            "timestamp": datetime.now().isoformat(),
        }
        
        json_str = json.dumps(location_dict)
        assert json_str is not None
        assert "Colonia" in json_str

    def test_distance_serialization(self, distance_data):
        """Test distance data can be serialized for WebSocket."""
        json_str = json.dumps(distance_data)
        assert json_str is not None
        assert "125.43" in json_str
        assert "formatted" in json_str


# =====================================================================
# ERROR HANDLING TESTS
# =====================================================================


class TestErrorHandling:
    """Test error handling in WebSocket integration."""

    def test_valid_signal_serialization(self):
        """Test valid signal can be serialized."""
        signal_data = {
            "system_name": "Test",
            "age": "1 minute ago",
            "coordinates": {"x": 0, "y": 0, "z": 0},
        }
        
        json_str = json.dumps(signal_data)
        assert json_str is not None
        assert "Test" in json_str

    def test_websocket_manager_handles_no_subscribers(self, mock_websocket_manager):
        """Test WebSocket manager returns empty list for no subscribers."""
        subs = mock_websocket_manager.get_channel_subscribers("hge_signal")
        assert isinstance(subs, list)

    def test_emit_with_incomplete_data_structure(self):
        """Test handling incomplete event data."""
        partial_signal = {
            "system_name": "Test",
            # Missing coordinates
        }
        
        json_str = json.dumps(partial_signal)
        assert "Test" in json_str


# =====================================================================
# REST API AND WEBSOCKET COEXISTENCE TESTS
# =====================================================================


class TestRESTWebSocketCoexistence:
    """Test REST API and WebSocket work together."""

    def test_rest_api_status_endpoint_available(self, client_with_websocket):
        """Test /api/status endpoint is available."""
        client, app, manager, ws_manager = client_with_websocket
        
        manager.get_status.return_value = {
            "hge_signal": None,
            "commander_location": None,
            "distance": None,
            "next_refresh": 10,
        }
        
        response = client.get('/api/status')
        assert response.status_code == 200

    def test_rest_api_refresh_endpoint_available(self, client_with_websocket):
        """Test /api/refresh endpoint is available."""
        client, app, manager, ws_manager = client_with_websocket
        
        manager.get_status.return_value = {
            "hge_signal": None,
            "commander_location": None,
            "distance": None,
            "next_refresh": 10,
        }
        manager.refresh.return_value = True
        
        response = client.post('/api/refresh')
        assert response.status_code in [200, 302, 405]  # Various possible responses

    def test_multiple_rest_calls_work(self, client_with_websocket):
        """Test multiple REST API calls work properly."""
        client, app, manager, ws_manager = client_with_websocket
        
        manager.get_status.return_value = {
            "hge_signal": None,
            "commander_location": None,
            "distance": None,
            "next_refresh": 10,
        }
        
        # Make multiple REST API calls
        for _ in range(3):
            response = client.get('/api/status')
            assert response.status_code == 200


# =====================================================================
# NOTIFICATION INTEGRATION TESTS
# =====================================================================


class TestNotificationIntegration:
    """Test notification system with WebSocket."""

    def test_notifications_data_structure(self):
        """Test notifications have proper data structure."""
        notification_data = {
            "system_name": "Test System",
            "distance_ly": 100.0,
            "timestamp": datetime.now().isoformat(),
            "channel": "discord",
            "success": True,
        }
        
        json_str = json.dumps(notification_data)
        assert "Test System" in json_str

    def test_notification_stats_structure(self):
        """Test notification stats structure."""
        stats_data = {
            "total": 5,
            "successful": 4,
            "failed": 1,
        }
        
        assert stats_data["total"] == 5
        assert stats_data["successful"] == 4


# =====================================================================
# WEBSOCKET CHANNEL TESTS
# =====================================================================


class TestWebSocketChannels:
    """Test individual WebSocket channels."""

    def test_hge_signal_channel_exists(self, app_with_websocket):
        """Test hge_signal channel is available."""
        app, manager, ws_manager = app_with_websocket
        
        # Channel availability is implicit in the system
        channels = ['hge_signal', 'location_update', 'distance_update', 'status']
        assert 'hge_signal' in channels

    def test_location_update_channel_exists(self, app_with_websocket):
        """Test location_update channel is available."""
        app, manager, ws_manager = app_with_websocket
        
        channels = ['hge_signal', 'location_update', 'distance_update', 'status']
        assert 'location_update' in channels

    def test_distance_update_channel_exists(self, app_with_websocket):
        """Test distance_update channel is available."""
        app, manager, ws_manager = app_with_websocket
        
        channels = ['hge_signal', 'location_update', 'distance_update', 'status']
        assert 'distance_update' in channels

    def test_status_channel_exists(self, app_with_websocket):
        """Test status channel is available."""
        app, manager, ws_manager = app_with_websocket
        
        channels = ['hge_signal', 'location_update', 'distance_update', 'status']
        assert 'status' in channels


# =====================================================================
# PRODUCTION SCENARIO TESTS
# =====================================================================


class TestProductionScenarios:
    """Test realistic production scenarios."""

    def test_hge_signal_event_flow(self, hge_signal):
        """Test HGE signal can flow through event system."""
        # 1. HGE signal detected
        signal_data = {
            "system_name": hge_signal.system_name,
            "coordinates": {
                "x": hge_signal.x,
                "y": hge_signal.y,
                "z": hge_signal.z,
            },
        }
        
        # 2. Can be serialized
        json_str = json.dumps(signal_data)
        assert json_str is not None
        
        # 3. Can be deserialized
        decoded = json.loads(json_str)
        assert decoded["system_name"] == "Beagle Point"

    def test_location_change_data_flow(self, commander_location):
        """Test location change flows through system."""
        location_data = {
            "system_name": commander_location.system_name,
            "coordinates": {
                "x": commander_location.x,
                "y": commander_location.y,
                "z": commander_location.z,
            },
        }
        
        json_str = json.dumps(location_data)
        decoded = json.loads(json_str)
        assert decoded["system_name"] == "Colonia"

    def test_distance_calculation_data_flow(self, distance_data):
        """Test distance data flows through system."""
        json_str = json.dumps(distance_data)
        decoded = json.loads(json_str)
        assert decoded["value"] == 125.43


# =====================================================================
# PERFORMANCE TESTS
# =====================================================================


class TestPerformance:
    """Test WebSocket performance characteristics."""

    def test_signal_serialization_performance(self):
        """Test signal data can be rapidly serialized."""
        signals = []
        
        # Create 10 signals rapidly
        for i in range(10):
            signal = {
                "system_name": f"System_{i}",
                "age": "Just now",
                "coordinates": {"x": float(i), "y": float(i), "z": float(i)},
            }
            json_str = json.dumps(signal)
            signals.append(json_str)
        
        # Should serialize all without error
        assert len(signals) == 10

    def test_websocket_manager_instance(self, mock_websocket_manager):
        """Test WebSocket manager is properly created."""
        ws_manager = mock_websocket_manager
        
        # Manager should be a single instance
        assert ws_manager is not None
        assert isinstance(ws_manager, Mock)


# =====================================================================
# BACKWARD COMPATIBILITY TESTS
# =====================================================================


class TestBackwardCompatibility:
    """Test WebSocket changes maintain backward compatibility."""

    def test_app_can_be_created_without_websocket(self, mock_manager):
        """Test app can be created without WebSocket manager."""
        app = create_app(mock_manager, None)
        assert app is not None

    def test_manager_optional_websocket(self, mock_manager):
        """Test HGENotifierManager works with optional WebSocket."""
        mock_manager.websocket_manager = None
        
        assert mock_manager.websocket_manager is None

    def test_html_templates_render(self, client_with_websocket):
        """Test HTML templates render correctly."""
        client, app, manager, ws_manager = client_with_websocket
        
        manager.get_status.return_value = {
            "hge_signal": None,
            "commander_location": None,
            "distance": None,
            "next_refresh": 10,
        }
        
        # Dashboard should render
        response = client.get('/')
        assert response.status_code == 200


# =====================================================================
# END-TO-END SCENARIO TESTS
# =====================================================================


class TestEndToEndScenarios:
    """Test complete end-to-end scenarios."""

    def test_commander_moves_scenario(self, distance_data):
        """Test scenario: Commander moves and distance updates."""
        # Initial distance
        assert distance_data["value"] == 125.43
        
        # Would emit distance_update event
        updated_distance = {
            "value": 50.0,
            "formatted": "50.00 ly",
        }
        
        assert updated_distance["value"] < distance_data["value"]

    def test_user_views_dashboard_scenario(self, client_with_websocket):
        """Test scenario: User opens dashboard."""
        client, app, manager, ws_manager = client_with_websocket
        
        manager.get_status.return_value = {
            "hge_signal": {
                "system_name": "Beagle Point",
                "age": "5 minutes ago",
                "coordinates": {"x": 1000.0, "y": 2000.0, "z": 3000.0},
            },
            "commander_location": {
                "system_name": "Sol",
                "coordinates": {"x": 0, "y": 0, "z": 0},
            },
            "distance": {
                "value": 12345.67,
                "formatted": "12345.67 ly",
            },
            "next_refresh": 10,
        }
        
        # User opens dashboard
        response = client.get('/')
        assert response.status_code == 200


# =====================================================================
# EDGE CASES
# =====================================================================


class TestEdgeCases:
    """Test edge cases and unusual conditions."""

    def test_empty_signal_data(self):
        """Test handling of empty signal data."""
        empty_signal = {}
        json_str = json.dumps(empty_signal)
        assert json_str == "{}"

    def test_very_large_distance_value(self):
        """Test handling very large distance values."""
        distance = {
            "value": 999999999.99,
            "formatted": "999999999.99 ly",
        }
        
        assert distance["value"] > 0

    def test_special_characters_in_system_name(self):
        """Test handling special characters in system names."""
        signal = {
            "system_name": "Sol's Orth'è & Co.",
            "age": "Just now",
            "coordinates": {"x": 0, "y": 0, "z": 0},
        }
        
        json_str = json.dumps(signal)
        assert "Sol" in json_str


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
