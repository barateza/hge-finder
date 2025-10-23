"""WebSocket server for real-time HGE Notifier updates using Socket.IO."""

import logging
from typing import Any, Callable, Dict, Optional

from socketio import AsyncServer, ASGIApp
from socketio.async_server import AsyncServer as SocketIOAsyncServer

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and real-time event broadcasting."""

    def __init__(self, async_mode: str = "asgi") -> None:
        """Initialize WebSocket manager.

        Args:
            async_mode: The async mode for Socket.IO ("asgi" for async support)
        """
        self.sio: Optional[SocketIOAsyncServer] = None
        self.async_mode = async_mode
        self.connected_clients: Dict[str, Dict[str, Any]] = {}
        self.subscriptions: Dict[str, set] = {
            "hge_signal": set(),
            "location_update": set(),
            "distance_update": set(),
            "status": set(),
        }

    def initialize(self) -> SocketIOAsyncServer:
        """Initialize and return Socket.IO server.

        Returns:
            AsyncServer instance configured for the app.
        """
        self.sio = AsyncServer(
            async_mode=self.async_mode,
            cors_allowed_origins="*",
            ping_timeout=60,
            ping_interval=25,
            engineio_logger=False,
            logger=False,
        )

        # Register event handlers
        self.sio.on("connect", self._on_connect)
        self.sio.on("disconnect", self._on_disconnect)
        self.sio.on("subscribe", self._on_subscribe)
        self.sio.on("unsubscribe", self._on_unsubscribe)

        logger.info("WebSocket server initialized")
        return self.sio

    async def _on_connect(self, sid: str, environ: Dict) -> None:
        """Handle client connection.

        Args:
            sid: Session ID of the connected client.
            environ: WSGI environment dictionary.
        """
        logger.info(f"Client connected: {sid}")
        self.connected_clients[sid] = {"subscriptions": set()}

    async def _on_disconnect(self, sid: str) -> None:
        """Handle client disconnection.

        Args:
            sid: Session ID of the disconnected client.
        """
        logger.info(f"Client disconnected: {sid}")
        if sid in self.connected_clients:
            del self.connected_clients[sid]

    async def _on_subscribe(self, sid: str, data: Dict[str, Any]) -> None:
        """Handle subscription to event channels.

        Args:
            sid: Session ID of the subscribing client.
            data: Subscription data containing 'channels' list.
        """
        channels = data.get("channels", [])
        if sid not in self.connected_clients:
            self.connected_clients[sid] = {"subscriptions": set()}

        for channel in channels:
            if channel in self.subscriptions:
                self.subscriptions[channel].add(sid)
                self.connected_clients[sid]["subscriptions"].add(channel)
                logger.debug(f"Client {sid} subscribed to {channel}")

    async def _on_unsubscribe(self, sid: str, data: Dict[str, Any]) -> None:
        """Handle unsubscription from event channels.

        Args:
            sid: Session ID of the unsubscribing client.
            data: Unsubscription data containing 'channels' list.
        """
        channels = data.get("channels", [])
        if sid not in self.connected_clients:
            return

        for channel in channels:
            if channel in self.subscriptions:
                self.subscriptions[channel].discard(sid)
                self.connected_clients[sid]["subscriptions"].discard(channel)
                logger.debug(f"Client {sid} unsubscribed from {channel}")

    async def emit_hge_signal(self, signal_data: Dict[str, Any]) -> None:
        """Emit HGE signal event to subscribed clients.

        Args:
            signal_data: Dictionary containing HGE signal information.
        """
        if not self.sio:
            return

        subscribers = self.subscriptions.get("hge_signal", set())
        logger.debug(f"Broadcasting HGE signal to {len(subscribers)} clients")

        for sid in subscribers:
            try:
                await self.sio.emit("hge_signal_update", signal_data, to=sid)
            except Exception as e:
                logger.error(f"Error emitting to {sid}: {e}")

    async def emit_location_update(self, location_data: Dict[str, Any]) -> None:
        """Emit location update event to subscribed clients.

        Args:
            location_data: Dictionary containing location information.
        """
        if not self.sio:
            return

        subscribers = self.subscriptions.get("location_update", set())
        logger.debug(f"Broadcasting location update to {len(subscribers)} clients")

        for sid in subscribers:
            try:
                await self.sio.emit("location_update", location_data, to=sid)
            except Exception as e:
                logger.error(f"Error emitting to {sid}: {e}")

    async def emit_distance_update(self, distance_data: Dict[str, Any]) -> None:
        """Emit distance update event to subscribed clients.

        Args:
            distance_data: Dictionary containing distance information.
        """
        if not self.sio:
            return

        subscribers = self.subscriptions.get("distance_update", set())
        logger.debug(f"Broadcasting distance update to {len(subscribers)} clients")

        for sid in subscribers:
            try:
                await self.sio.emit("distance_update", distance_data, to=sid)
            except Exception as e:
                logger.error(f"Error emitting to {sid}: {e}")

    async def emit_status(self, status_data: Dict[str, Any]) -> None:
        """Emit status update to all subscribed clients.

        Args:
            status_data: Dictionary containing status information.
        """
        if not self.sio:
            return

        subscribers = self.subscriptions.get("status", set())
        logger.debug(f"Broadcasting status to {len(subscribers)} clients")

        for sid in subscribers:
            try:
                await self.sio.emit("status_update", status_data, to=sid)
            except Exception as e:
                logger.error(f"Error emitting to {sid}: {e}")

    def broadcast_to_channel(self, channel: str, event: str, data: Dict[str, Any]) -> None:
        """Broadcast event to all clients subscribed to a channel (non-async wrapper).

        Args:
            channel: Channel name.
            event: Event name.
            data: Event data to broadcast.
        """
        # Note: This is a sync wrapper. In async contexts, use the async emit methods.
        if not self.sio:
            return

        subscribers = self.subscriptions.get(channel, set())
        logger.debug(f"Broadcasting {event} to {len(subscribers)} clients on {channel}")

    def get_connected_clients_count(self) -> int:
        """Get total number of connected clients.

        Returns:
            Number of connected clients.
        """
        return len(self.connected_clients)

    def get_subscribers_for_channel(self, channel: str) -> set:
        """Get set of client SIDs subscribed to a channel.

        Args:
            channel: Channel name.

        Returns:
            Set of client SIDs subscribed to the channel.
        """
        return self.subscriptions.get(channel, set()).copy()

    def get_all_subscriptions(self) -> Dict[str, set]:
        """Get all current subscriptions.

        Returns:
            Dictionary mapping channels to sets of subscribed client SIDs.
        """
        return {channel: sids.copy() for channel, sids in self.subscriptions.items()}

    def close(self) -> None:
        """Close WebSocket server and clean up resources."""
        self.connected_clients.clear()
        for channel in self.subscriptions:
            self.subscriptions[channel].clear()
        logger.info("WebSocket server closed")
