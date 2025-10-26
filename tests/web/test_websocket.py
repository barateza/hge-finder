"""Unit tests for WebSocket functionality."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.web.websocket import WebSocketManager


@pytest.fixture
def ws_manager():
    """Create a WebSocketManager instance for testing."""
    return WebSocketManager(async_mode="asgi")


@pytest.fixture
def initialized_ws_manager(ws_manager):
    """Create an initialized WebSocketManager."""
    ws_manager.initialize()
    return ws_manager


class TestWebSocketManagerInitialization:
    """Test WebSocket manager initialization."""

    def test_websocket_manager_creation(self, ws_manager):
        """Test WebSocket manager is created with default settings."""
        assert ws_manager is not None
        assert ws_manager.async_mode == "asgi"
        assert ws_manager.sio is None
        assert len(ws_manager.connected_clients) == 0

    def test_websocket_manager_initialization(self, ws_manager):
        """Test WebSocket manager initialization."""
        sio = ws_manager.initialize()
        assert sio is not None
        assert ws_manager.sio is not None
        assert isinstance(ws_manager.subscriptions, dict)
        assert "hge_signal" in ws_manager.subscriptions
        assert "location_update" in ws_manager.subscriptions
        assert "distance_update" in ws_manager.subscriptions
        assert "status" in ws_manager.subscriptions

    def test_websocket_channels_initialized(self, initialized_ws_manager):
        """Test all WebSocket channels are properly initialized."""
        channels = ["hge_signal", "location_update", "distance_update", "status"]
        for channel in channels:
            assert channel in initialized_ws_manager.subscriptions
            assert isinstance(initialized_ws_manager.subscriptions[channel], set)
            assert len(initialized_ws_manager.subscriptions[channel]) == 0


class TestWebSocketConnectionHandling:
    """Test WebSocket connection and disconnection."""

    @pytest.mark.asyncio
    async def test_client_connection(self, initialized_ws_manager):
        """Test client connection handling."""
        await initialized_ws_manager._on_connect("test_sid_1", {})
        assert "test_sid_1" in initialized_ws_manager.connected_clients
        assert initialized_ws_manager.get_connected_clients_count() == 1

    @pytest.mark.asyncio
    async def test_client_disconnection(self, initialized_ws_manager):
        """Test client disconnection handling."""
        await initialized_ws_manager._on_connect("test_sid_1", {})
        assert initialized_ws_manager.get_connected_clients_count() == 1
        
        await initialized_ws_manager._on_disconnect("test_sid_1")
        assert "test_sid_1" not in initialized_ws_manager.connected_clients
        assert initialized_ws_manager.get_connected_clients_count() == 0

    @pytest.mark.asyncio
    async def test_multiple_client_connections(self, initialized_ws_manager):
        """Test multiple client connections."""
        sids = ["client_1", "client_2", "client_3"]
        for sid in sids:
            await initialized_ws_manager._on_connect(sid, {})
        
        assert initialized_ws_manager.get_connected_clients_count() == 3
        for sid in sids:
            assert sid in initialized_ws_manager.connected_clients


class TestWebSocketSubscriptions:
    """Test WebSocket subscription functionality."""

    @pytest.mark.asyncio
    async def test_client_subscription(self, initialized_ws_manager):
        """Test client subscribing to channels."""
        await initialized_ws_manager._on_connect("test_sid", {})
        
        data = {"channels": ["hge_signal", "distance_update"]}
        await initialized_ws_manager._on_subscribe("test_sid", data)
        
        assert "test_sid" in initialized_ws_manager.subscriptions["hge_signal"]
        assert "test_sid" in initialized_ws_manager.subscriptions["distance_update"]
        assert "test_sid" not in initialized_ws_manager.subscriptions["location_update"]

    @pytest.mark.asyncio
    async def test_client_unsubscription(self, initialized_ws_manager):
        """Test client unsubscribing from channels."""
        await initialized_ws_manager._on_connect("test_sid", {})
        
        # Subscribe first
        subscribe_data = {"channels": ["hge_signal"]}
        await initialized_ws_manager._on_subscribe("test_sid", subscribe_data)
        assert "test_sid" in initialized_ws_manager.subscriptions["hge_signal"]
        
        # Unsubscribe
        unsubscribe_data = {"channels": ["hge_signal"]}
        await initialized_ws_manager._on_unsubscribe("test_sid", unsubscribe_data)
        assert "test_sid" not in initialized_ws_manager.subscriptions["hge_signal"]

    @pytest.mark.asyncio
    async def test_subscription_to_all_channels(self, initialized_ws_manager):
        """Test client subscribing to all channels."""
        await initialized_ws_manager._on_connect("test_sid", {})
        
        all_channels = ["hge_signal", "location_update", "distance_update", "status"]
        data = {"channels": all_channels}
        await initialized_ws_manager._on_subscribe("test_sid", data)
        
        for channel in all_channels:
            assert "test_sid" in initialized_ws_manager.subscriptions[channel]

    @pytest.mark.asyncio
    async def test_multiple_clients_subscription(self, initialized_ws_manager):
        """Test multiple clients subscribing to same channel."""
        sids = ["client_1", "client_2", "client_3"]
        for sid in sids:
            await initialized_ws_manager._on_connect(sid, {})
        
        data = {"channels": ["hge_signal"]}
        for sid in sids:
            await initialized_ws_manager._on_subscribe(sid, data)
        
        subscribers = initialized_ws_manager.get_subscribers_for_channel("hge_signal")
        assert len(subscribers) == 3
        for sid in sids:
            assert sid in subscribers


class TestWebSocketEventEmission:
    """Test WebSocket event emission."""

    @pytest.mark.asyncio
    async def test_emit_hge_signal(self, initialized_ws_manager):
        """Test emitting HGE signal event."""
        await initialized_ws_manager._on_connect("test_sid", {})
        data = {"channels": ["hge_signal"]}
        await initialized_ws_manager._on_subscribe("test_sid", data)
        
        signal_data = {
            "system_name": "Sol",
            "distance_ly": 10.5,
            "timestamp": "2024-01-01T00:00:00",
        }
        
        # Mock the sio.emit method
        initialized_ws_manager.sio.emit = AsyncMock()
        
        await initialized_ws_manager.emit_hge_signal(signal_data)
        initialized_ws_manager.sio.emit.assert_called_once()

    @pytest.mark.asyncio
    async def test_emit_location_update(self, initialized_ws_manager):
        """Test emitting location update event."""
        await initialized_ws_manager._on_connect("test_sid", {})
        data = {"channels": ["location_update"]}
        await initialized_ws_manager._on_subscribe("test_sid", data)
        
        location_data = {
            "system_name": "Sirius",
            "timestamp": "2024-01-01T00:00:00",
        }
        
        # Mock the sio.emit method
        initialized_ws_manager.sio.emit = AsyncMock()
        
        await initialized_ws_manager.emit_location_update(location_data)
        initialized_ws_manager.sio.emit.assert_called_once()

    @pytest.mark.asyncio
    async def test_emit_distance_update(self, initialized_ws_manager):
        """Test emitting distance update event."""
        await initialized_ws_manager._on_connect("test_sid", {})
        data = {"channels": ["distance_update"]}
        await initialized_ws_manager._on_subscribe("test_sid", data)
        
        distance_data = {
            "distance_ly": 25.5,
            "formatted": "25.50 ly",
        }
        
        # Mock the sio.emit method
        initialized_ws_manager.sio.emit = AsyncMock()
        
        await initialized_ws_manager.emit_distance_update(distance_data)
        initialized_ws_manager.sio.emit.assert_called_once()

    @pytest.mark.asyncio
    async def test_emit_status(self, initialized_ws_manager):
        """Test emitting status event."""
        await initialized_ws_manager._on_connect("test_sid", {})
        data = {"channels": ["status"]}
        await initialized_ws_manager._on_subscribe("test_sid", data)
        
        status_data = {
            "initialized": True,
            "hge_signal": {"system_name": "Sol"},
            "commander_location": {"system_name": "Sirius"},
        }
        
        # Mock the sio.emit method
        initialized_ws_manager.sio.emit = AsyncMock()
        
        await initialized_ws_manager.emit_status(status_data)
        initialized_ws_manager.sio.emit.assert_called_once()


class TestWebSocketUtilityMethods:
    """Test WebSocket utility methods."""

    @pytest.mark.asyncio
    async def test_get_connected_clients_count(self, initialized_ws_manager):
        """Test getting connected clients count."""
        assert initialized_ws_manager.get_connected_clients_count() == 0
        
        for i in range(3):
            await initialized_ws_manager._on_connect(f"client_{i}", {})
        
        assert initialized_ws_manager.get_connected_clients_count() == 3

    def test_get_subscribers_for_channel(self, initialized_ws_manager):
        """Test getting subscribers for a specific channel."""
        # Add some subscribers
        initialized_ws_manager.subscriptions["hge_signal"].add("client_1")
        initialized_ws_manager.subscriptions["hge_signal"].add("client_2")
        
        subscribers = initialized_ws_manager.get_subscribers_for_channel("hge_signal")
        assert len(subscribers) == 2
        assert "client_1" in subscribers
        assert "client_2" in subscribers

    def test_get_all_subscriptions(self, initialized_ws_manager):
        """Test getting all subscriptions."""
        # Add some subscriptions
        initialized_ws_manager.subscriptions["hge_signal"].add("client_1")
        initialized_ws_manager.subscriptions["location_update"].add("client_2")
        
        all_subs = initialized_ws_manager.get_all_subscriptions()
        assert isinstance(all_subs, dict)
        assert "client_1" in all_subs["hge_signal"]
        assert "client_2" in all_subs["location_update"]

    def test_websocket_manager_close(self, initialized_ws_manager):
        """Test closing WebSocket manager."""
        initialized_ws_manager.connected_clients["test_sid"] = {"subscriptions": set()}
        initialized_ws_manager.subscriptions["hge_signal"].add("test_sid")
        
        initialized_ws_manager.close()
        
        assert len(initialized_ws_manager.connected_clients) == 0
        for channel in initialized_ws_manager.subscriptions:
            assert len(initialized_ws_manager.subscriptions[channel]) == 0


class TestWebSocketErrorHandling:
    """Test WebSocket error handling."""

    @pytest.mark.asyncio
    async def test_unsubscribe_without_connect(self, initialized_ws_manager):
        """Test unsubscribing without being connected."""
        data = {"channels": ["hge_signal"]}
        # Should not raise an error
        await initialized_ws_manager._on_unsubscribe("unknown_sid", data)

    @pytest.mark.asyncio
    async def test_emit_with_no_subscribers(self, initialized_ws_manager):
        """Test emitting event with no subscribers."""
        signal_data = {"system_name": "Sol"}
        # Mock the sio.emit method
        initialized_ws_manager.sio.emit = AsyncMock()
        
        # Should not raise an error
        await initialized_ws_manager.emit_hge_signal(signal_data)

    @pytest.mark.asyncio
    async def test_emit_to_disconnected_client(self, initialized_ws_manager):
        """Test emitting to a client that has already disconnected."""
        await initialized_ws_manager._on_connect("test_sid", {})
        data = {"channels": ["hge_signal"]}
        await initialized_ws_manager._on_subscribe("test_sid", data)
        
        # Disconnect but leave subscription (simulate race condition)
        await initialized_ws_manager._on_disconnect("test_sid")
        
        signal_data = {"system_name": "Sol"}
        # Mock the sio.emit method to simulate error
        initialized_ws_manager.sio.emit = AsyncMock(side_effect=Exception("Client disconnected"))
        
        # Should handle the error gracefully
        await initialized_ws_manager.emit_hge_signal(signal_data)
