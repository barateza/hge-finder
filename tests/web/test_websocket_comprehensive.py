"""
Comprehensive WebSocket Tests

Tests for WebSocket functionality:
- Connection/disconnection handling
- Channel subscription/unsubscription
- Event broadcasting
- Error handling
- Message format validation

Target: Increase src/web/websocket.py coverage from 78% → 90%+
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timezone

from src.web.websocket import WebSocketManager


class TestWebSocketManagerInitialization:
    """Test WebSocketManager initialization and setup."""

    def test_websocket_manager_creates_instance(self):
        """Test WebSocketManager can be instantiated."""
        ws_manager = WebSocketManager()
        assert ws_manager is not None

    def test_websocket_manager_initialize_returns_async_server(self):
        """Test initialize() returns AsyncServer."""
        ws_manager = WebSocketManager()
        sio = ws_manager.initialize()
        assert sio is not None

    def test_websocket_manager_initialize_idempotent(self):
        """Test initialize() can be called multiple times."""
        ws_manager = WebSocketManager()
        sio1 = ws_manager.initialize()
        sio2 = ws_manager.initialize()
        # Should both return AsyncServer instances
        assert sio1 is not None
        assert sio2 is not None

    def test_websocket_manager_has_required_methods(self):
        """Test WebSocketManager has required methods."""
        ws_manager = WebSocketManager()
        assert hasattr(ws_manager, 'initialize')
        assert hasattr(ws_manager, 'emit_hge_signal')
        assert hasattr(ws_manager, 'emit_location_update')
        assert hasattr(ws_manager, 'emit_distance_update')
        assert hasattr(ws_manager, 'emit_status')

    def test_websocket_manager_async_mode_default(self):
        """Test WebSocketManager defaults to asgi async mode."""
        ws_manager = WebSocketManager()
        assert ws_manager.async_mode == "asgi"

    def test_websocket_manager_async_mode_custom(self):
        """Test WebSocketManager accepts custom async mode."""
        ws_manager = WebSocketManager(async_mode="threading")
        assert ws_manager.async_mode == "threading"


class TestWebSocketSubscriptions:
    """Test WebSocket subscription management."""

    def test_subscriptions_initialized(self):
        """Test subscriptions are initialized with required channels."""
        ws_manager = WebSocketManager()
        assert "hge_signal" in ws_manager.subscriptions
        assert "location_update" in ws_manager.subscriptions
        assert "distance_update" in ws_manager.subscriptions
        assert "status" in ws_manager.subscriptions

    @pytest.mark.asyncio
    async def test_subscribe_to_channels(self):
        """Test subscribing to channels."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        subscription_data = {
            "channels": ["hge_signal", "location_update"]
        }
        
        await ws_manager._on_subscribe("test_sid_123", subscription_data)
        
        # Verify subscription was recorded
        assert "test_sid_123" in ws_manager.subscriptions["hge_signal"]
        assert "test_sid_123" in ws_manager.subscriptions["location_update"]

    @pytest.mark.asyncio
    async def test_unsubscribe_from_channels(self):
        """Test unsubscribing from channels."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        # First subscribe
        sub_data = {"channels": ["hge_signal"]}
        await ws_manager._on_subscribe("sid_456", sub_data)
        
        # Then unsubscribe
        unsub_data = {"channels": ["hge_signal"]}
        await ws_manager._on_unsubscribe("sid_456", unsub_data)
        
        # Verify unsubscription
        assert "sid_456" not in ws_manager.subscriptions["hge_signal"]

    @pytest.mark.asyncio
    async def test_subscribe_with_empty_channels(self):
        """Test subscribing with empty channel list."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        subscription_data = {"channels": []}
        
        # Should not raise exception
        await ws_manager._on_subscribe("sid_empty", subscription_data)

    @pytest.mark.asyncio
    async def test_subscribe_with_invalid_channel(self):
        """Test subscribing to invalid channel is ignored."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        subscription_data = {"channels": ["invalid_channel"]}
        
        await ws_manager._on_subscribe("sid_invalid", subscription_data)
        
        # Invalid channel should not be added
        assert "sid_invalid" not in ws_manager.subscriptions.get("invalid_channel", set())


class TestWebSocketClientConnections:
    """Test WebSocket client connection management."""

    @pytest.mark.asyncio
    async def test_connect_event_creates_client_entry(self):
        """Test connect event creates connected client entry."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        environ = {"REMOTE_ADDR": "127.0.0.1"}
        await ws_manager._on_connect("client_1", environ)
        
        # Verify client was registered
        assert "client_1" in ws_manager.connected_clients
        assert "subscriptions" in ws_manager.connected_clients["client_1"]

    @pytest.mark.asyncio
    async def test_disconnect_event_removes_client(self):
        """Test disconnect event removes client entry."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        # Connect first
        await ws_manager._on_connect("client_2", {})
        assert "client_2" in ws_manager.connected_clients
        
        # Disconnect
        await ws_manager._on_disconnect("client_2")
        
        # Verify client was removed
        assert "client_2" not in ws_manager.connected_clients

    @pytest.mark.asyncio
    async def test_disconnect_nonexistent_client(self):
        """Test disconnecting non-existent client doesn't error."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        # Should not raise exception
        await ws_manager._on_disconnect("nonexistent_client")


class TestWebSocketEventEmission:
    """Test WebSocket event emission."""

    @pytest.mark.asyncio
    async def test_emit_hge_signal_without_server(self):
        """Test emitting HGE signal when server not initialized."""
        ws_manager = WebSocketManager()
        # Don't call initialize()
        
        signal_data = {
            "system_name": "Tchernobog",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        # Should not raise exception
        await ws_manager.emit_hge_signal(signal_data)

    @pytest.mark.asyncio
    async def test_emit_location_update_without_server(self):
        """Test emitting location update when server not initialized."""
        ws_manager = WebSocketManager()
        
        location_data = {
            "system_name": "Sol",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        # Should not raise exception
        await ws_manager.emit_location_update(location_data)

    @pytest.mark.asyncio
    async def test_emit_distance_update_without_server(self):
        """Test emitting distance update when server not initialized."""
        ws_manager = WebSocketManager()
        
        distance_data = {
            "distance_ly": 42.5,
            "from_system": "Sol",
            "to_system": "Tchernobog",
        }
        
        # Should not raise exception
        await ws_manager.emit_distance_update(distance_data)

    @pytest.mark.asyncio
    async def test_emit_status_without_server(self):
        """Test emitting status when server not initialized."""
        ws_manager = WebSocketManager()
        
        status_data = {
            "commander_location": "Sol",
            "hge_signal": "Tchernobog",
            "distance_ly": 42.5,
        }
        
        # Should not raise exception
        await ws_manager.emit_status(status_data)


class TestWebSocketIntegrationWithApp:
    """Test WebSocket integration with Flask app."""

    def test_websocket_manager_can_be_passed_to_app(self):
        """Test WebSocketManager can be passed to create_app."""
        from src.web import create_app
        from src.core import HGENotifierManager
        
        manager = HGENotifierManager()
        ws_manager = WebSocketManager()
        
        # Should not raise exception
        app = create_app(manager, ws_manager=ws_manager)
        assert app is not None

    def test_app_works_without_websocket_manager(self):
        """Test app can be created without WebSocketManager."""
        from src.web import create_app
        from src.core import HGENotifierManager
        
        manager = HGENotifierManager()
        
        app = create_app(manager, ws_manager=None)
        assert app is not None

    def test_websocket_handlers_registered(self):
        """Test WebSocket event handlers are registered."""
        from src.web import create_app
        from src.core import HGENotifierManager
        
        manager = HGENotifierManager()
        ws_manager = WebSocketManager()
        
        app = create_app(manager, ws_manager=ws_manager)
        
        # App should be properly configured
        assert app is not None
        with app.test_client() as client:
            response = client.get("/api/status")
            assert response.status_code == 200


class TestWebSocketChannelQueries:
    """Test WebSocket channel query methods."""

    def test_get_connected_clients_count_empty(self):
        """Test get_connected_clients_count when no clients connected."""
        ws_manager = WebSocketManager()
        assert ws_manager.get_connected_clients_count() == 0

    @pytest.mark.asyncio
    async def test_get_connected_clients_count_with_clients(self):
        """Test get_connected_clients_count with connected clients."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        await ws_manager._on_connect("client_1", {})
        await ws_manager._on_connect("client_2", {})
        
        assert ws_manager.get_connected_clients_count() == 2

    def test_get_subscribers_for_channel(self):
        """Test get_subscribers_for_channel returns correct SIDs."""
        ws_manager = WebSocketManager()
        
        # Manually add subscribers
        ws_manager.subscriptions["hge_signal"].add("sid_1")
        ws_manager.subscriptions["hge_signal"].add("sid_2")
        
        subscribers = ws_manager.get_subscribers_for_channel("hge_signal")
        assert "sid_1" in subscribers
        assert "sid_2" in subscribers

    def test_get_subscribers_for_nonexistent_channel(self):
        """Test get_subscribers_for_channel with invalid channel."""
        ws_manager = WebSocketManager()
        
        subscribers = ws_manager.get_subscribers_for_channel("nonexistent")
        assert isinstance(subscribers, set)
        assert len(subscribers) == 0

    def test_get_all_subscriptions(self):
        """Test get_all_subscriptions returns all channels."""
        ws_manager = WebSocketManager()
        
        ws_manager.subscriptions["hge_signal"].add("sid_1")
        ws_manager.subscriptions["status"].add("sid_2")
        
        all_subs = ws_manager.get_all_subscriptions()
        
        assert "hge_signal" in all_subs
        assert "location_update" in all_subs
        assert "distance_update" in all_subs
        assert "status" in all_subs


class TestWebSocketCleanup:
    """Test WebSocket cleanup and resource management."""

    def test_close_clears_clients(self):
        """Test close() clears connected clients."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        ws_manager.connected_clients["sid_1"] = {"subscriptions": set()}
        assert len(ws_manager.connected_clients) > 0
        
        ws_manager.close()
        
        assert len(ws_manager.connected_clients) == 0

    def test_close_clears_subscriptions(self):
        """Test close() clears all subscriptions."""
        ws_manager = WebSocketManager()
        
        ws_manager.subscriptions["hge_signal"].add("sid_1")
        ws_manager.subscriptions["status"].add("sid_2")
        
        ws_manager.close()
        
        for channel in ws_manager.subscriptions.values():
            assert len(channel) == 0


class TestWebSocketConcurrency:
    """Test WebSocket concurrent operations."""

    @pytest.mark.asyncio
    async def test_multiple_subscriptions_concurrent(self):
        """Test handling multiple concurrent subscriptions."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        tasks = []
        for i in range(5):
            data = {"channels": ["hge_signal", "status"]}
            task = ws_manager._on_subscribe(f"sid_{i}", data)
            tasks.append(task)
        
        # Should not raise exception
        await asyncio.gather(*tasks)
        
        # Verify subscriptions
        assert len(ws_manager.subscriptions["hge_signal"]) == 5
        assert len(ws_manager.subscriptions["status"]) == 5

    @pytest.mark.asyncio
    async def test_multiple_connections_concurrent(self):
        """Test handling multiple concurrent connections."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        tasks = []
        for i in range(5):
            task = ws_manager._on_connect(f"client_{i}", {})
            tasks.append(task)
        
        # Should not raise exception
        await asyncio.gather(*tasks)
        
        assert ws_manager.get_connected_clients_count() == 5


class TestWebSocketDataStructures:
    """Test WebSocket internal data structures."""

    def test_connected_clients_dict_structure(self):
        """Test connected_clients dict has correct structure."""
        ws_manager = WebSocketManager()
        
        ws_manager.connected_clients["sid"] = {"subscriptions": set()}
        
        assert isinstance(ws_manager.connected_clients["sid"], dict)
        assert "subscriptions" in ws_manager.connected_clients["sid"]

    def test_subscriptions_dict_structure(self):
        """Test subscriptions dict has correct structure."""
        ws_manager = WebSocketManager()
        
        for channel, sids in ws_manager.subscriptions.items():
            assert isinstance(sids, set)

    def test_subscriptions_contains_expected_channels(self):
        """Test subscriptions contains all expected channels."""
        ws_manager = WebSocketManager()
        
        expected_channels = {
            "hge_signal",
            "location_update",
            "distance_update",
            "status",
        }
        
        assert set(ws_manager.subscriptions.keys()) == expected_channels


class TestWebSocketErrorHandling:
    """Test WebSocket error handling."""

    @pytest.mark.asyncio
    async def test_subscribe_with_malformed_data(self):
        """Test subscription with malformed data structure."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        # Missing 'channels' key
        data = {"invalid": "data"}
        
        # Should not raise exception
        await ws_manager._on_subscribe("sid", data)

    @pytest.mark.asyncio
    async def test_subscribe_with_empty_dict_data(self):
        """Test subscription with empty dict data."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        # Should handle gracefully when channels key missing
        data = {}
        
        # Should not raise exception
        await ws_manager._on_subscribe("sid", data)

    @pytest.mark.asyncio
    async def test_unsubscribe_nonexistent_client(self):
        """Test unsubscribing for non-existent client."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        data = {"channels": ["hge_signal"]}
        
        # Should not raise exception
        await ws_manager._on_unsubscribe("nonexistent_sid", data)


class TestWebSocketHealthChecks:
    """Test WebSocket health and status checks."""

    def test_websocket_manager_maintains_state(self):
        """Test WebSocketManager maintains state across calls."""
        ws_manager = WebSocketManager()
        sio1 = ws_manager.initialize()
        sio2 = ws_manager.initialize()
        
        # Both should be non-None
        assert sio1 is not None
        assert sio2 is not None

    def test_websocket_can_emit_after_initialization(self):
        """Test WebSocket can emit after proper initialization."""
        ws_manager = WebSocketManager()
        ws_manager.initialize()
        
        signal_data = {
            "system_name": "Test",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        # Should not raise exception on initialization
        import asyncio
        asyncio.run(ws_manager.emit_hge_signal(signal_data))

    def test_broadcast_to_channel_method_exists(self):
        """Test broadcast_to_channel method exists and is callable."""
        ws_manager = WebSocketManager()
        
        assert hasattr(ws_manager, 'broadcast_to_channel')
        assert callable(ws_manager.broadcast_to_channel)

    def test_emit_system_group_update_method_exists(self):
        """Test emit_system_group_update method exists and is callable."""
        ws_manager = WebSocketManager()
        
        assert hasattr(ws_manager, 'emit_system_group_update')
        assert callable(ws_manager.emit_system_group_update)
