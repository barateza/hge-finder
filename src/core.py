"""Core manager orchestrating all components."""

import asyncio
import logging
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from src.web.websocket import WebSocketManager

from src.config.settings import get_settings
from src.distance import DistanceCalculator
from src.distance.coordinates import CoordinateDatabase
from src.eddn import EDDNMonitor, HGESignal
from src.journal import CommanderLocation, JournalParser
from src.notifications.manager import NotificationManager
from src.notifications.models import Alert


class HGENotifierManager:
    """Core manager orchestrating EDDN monitoring and location tracking."""

    def __init__(self, websocket_manager: Optional['WebSocketManager'] = None) -> None:
        """Initialize the HGE Notifier Manager.

        Args:
            websocket_manager: Optional WebSocket manager for real-time updates.
        """
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        self.websocket_manager = websocket_manager
        
        # Initialize coordinate database
        data_path = self.settings.project_root / "data"
        self.coord_db = CoordinateDatabase(db_path=data_path)
        
        # Initialize EDDN monitor with callback
        self.eddn_monitor = EDDNMonitor(
            mock_mode=self.settings.eddn_mock_mode,
            callback=self._on_new_hge_signal,
        )
        
        # Initialize journal parser with both location and HGE callbacks
        self.journal_parser = JournalParser(
            journal_path=self.settings.journal_path,
            callback=self._on_location_change,
            hge_callback=self._on_new_hge_signal,
        )
        
        self.distance_calculator = DistanceCalculator()
        
        # Initialize notification manager
        alert_config = Alert(
            max_distance_ly=self.settings.alert_max_distance,
            max_age_hours=int(self.settings.alert_max_age),
            enabled=self.settings.notifications_enabled,
        )
        self.notification_manager = NotificationManager(
            discord_webhook=self.settings.discord_webhook_url,
            alert_config=alert_config,
            cooldown_seconds=self.settings.notification_cooldown_seconds,
        )

        # Track signal history (keep last 100 signals)
        self.signal_history: deque = deque(maxlen=100)
        
        self._initialized = False

    def _on_new_hge_signal(self, signal: HGESignal) -> None:
        """Callback when new HGE signal is detected.

        Args:
            signal: The new HGE signal detected.
        """
        self.logger.info(f"New HGE signal in {signal.system_name}")

        # Add to signal history
        self.signal_history.append(signal)

        # Emit WebSocket event if manager is available (non-blocking, silently fails if no event loop)
        if self.websocket_manager:
            try:
                signal_data = self._format_signal(signal)
                if signal_data:
                    try:
                        # Try to get the running event loop
                        loop = asyncio.get_running_loop()
                        loop.create_task(self.websocket_manager.emit_hge_signal(signal_data))
                    except RuntimeError:
                        # No event loop in this thread - that's OK for sync callbacks
                        self.logger.debug("No event loop in current thread for WebSocket emit")
            except Exception as e:
                self.logger.debug(f"Error preparing WebSocket event: {e}")
        
        # Try to send notification if commander location is available
        try:
            location = self.journal_parser.get_latest_location()
            if location:
                # Enrich coordinates if needed
                enriched_signal = self._enrich_signal_coordinates(signal)
                enriched_location = self._enrich_location_coordinates(location)
                
                if enriched_signal and enriched_location:
                    # Check and send notification
                    notification = self.notification_manager.check_and_notify(enriched_signal, enriched_location)
                    if notification:
                        self.logger.info(f"Notification sent: {notification.signal_system} ({notification.distance_ly} ly)")
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")

    def _on_location_change(self, location: CommanderLocation) -> None:
        """Callback when commander location changes.

        Args:
            location: The commander's new location.
        """
        self.logger.info(f"Location changed to {location.system_name}")

        # Emit WebSocket event if manager is available
        # Note: These are async calls in a sync context, so we don't try to await them
        if self.websocket_manager:
            try:
                location_data = self._format_location(location)
                if location_data:
                    # Schedule async emit without awaiting (fire-and-forget)
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(self.websocket_manager.emit_location_update(location_data))
                    except RuntimeError:
                        # No event loop in this thread - skip WebSocket update
                        pass
                
                # Also emit distance update if we have a signal
                signal = self.eddn_monitor.get_latest_signal()
                if signal:
                    distance_data = self._calculate_distance(signal, location)
                    if distance_data:
                        try:
                            loop = asyncio.get_running_loop()
                            loop.create_task(self.websocket_manager.emit_distance_update(distance_data))
                        except RuntimeError:
                            pass
            except Exception as e:
                self.logger.debug(f"Error scheduling WebSocket event: {e}")

    def start(self) -> None:
        """Start monitoring EDDN and journal."""
        self.logger.info("Starting HGE Notifier Manager")
        self.eddn_monitor.start()
        self.journal_parser.start()
        self._initialized = True
        self.logger.info("HGE Notifier Manager started")

    def stop(self) -> None:
        """Stop monitoring."""
        self.logger.info("Stopping HGE Notifier Manager")
        self.eddn_monitor.stop()
        self.journal_parser.stop()
        self._initialized = False
        self.logger.info("HGE Notifier Manager stopped")

    def get_status(self) -> dict:
        """
        Get current status including HGE signal, location, distance, and notifications.

        Returns:
            Dictionary with current status.
        """
        signal = self.eddn_monitor.get_latest_signal()
        location = self.journal_parser.get_latest_location()

        # Fetch coordinates if missing
        signal = self._enrich_signal_coordinates(signal)
        location = self._enrich_location_coordinates(location)

        status = {
            "initialized": self._initialized,
            "hge_signal": self._format_signal(signal),
            "commander_location": self._format_location(location),
            "distance": self._calculate_distance(signal, location),
            "notifications": {
                "history": self._format_notification_history(),
                "stats": self._get_notification_stats(),
            },
        }

        return status

    def refresh(self) -> None:
        """Refresh data from EDDN and journal."""
        self.logger.debug("Refreshing data")
        # In a real implementation, this would trigger re-reads of journal and EDDN
        pass

    def _enrich_signal_coordinates(self, signal: Optional[HGESignal]) -> Optional[HGESignal]:
        """
        Enrich signal with coordinates if missing.

        Args:
            signal: HGE signal

        Returns:
            Signal with coordinates filled in if possible
        """
        if signal is None or (signal.x is not None and signal.y is not None and signal.z is not None):
            return signal

        try:
            coords = self.coord_db.get_coordinates(signal.system_name)
            if coords:
                signal.x, signal.y, signal.z = coords
        except Exception as e:
            self.logger.debug(f"Error fetching coordinates for {signal.system_name}: {e}")

        return signal

    def _enrich_location_coordinates(self, location: Optional[CommanderLocation]) -> Optional[CommanderLocation]:
        """
        Enrich location with coordinates if missing.

        Priority: use journal coordinates if available, fallback to EDSM.

        Args:
            location: Commander location

        Returns:
            Location with coordinates filled in if possible
        """
        if location is None:
            return location

        # If all coordinates are already present, return as-is
        if location.x is not None and location.y is not None and location.z is not None:
            return location

        # Try to get from database/EDSM if missing
        try:
            self.logger.debug(f"Attempting to enrich coordinates for {location.system_name}")
            coords = self.coord_db.get_coordinates(location.system_name)
            if coords:
                location.x, location.y, location.z = coords
                self.logger.debug(f"Enriched {location.system_name} with EDSM coordinates: {coords}")
            else:
                self.logger.debug(f"Could not find coordinates for {location.system_name} in EDSM")
        except Exception as e:
            self.logger.warning(f"Error fetching coordinates for {location.system_name}: {e}")

        return location

    @staticmethod
    def _format_signal(signal: Optional[HGESignal]) -> Optional[dict]:
        """Format HGE signal for display."""
        if signal is None:
            return None

        return {
            "system_name": signal.system_name,
            "timestamp": signal.timestamp.isoformat(),
            "age": signal.age_human_readable(),
            "coordinates": {
                "x": signal.x,
                "y": signal.y,
                "z": signal.z,
            },
        }

    @staticmethod
    def _format_location(location: Optional[CommanderLocation]) -> Optional[dict]:
        """Format commander location for display."""
        if location is None:
            return None

        return {
            "system_name": location.system_name,
            "timestamp": location.timestamp.isoformat(),
            "coordinates": {
                "x": location.x,
                "y": location.y,
                "z": location.z,
            },
        }

    def _calculate_distance(
        self,
        signal: Optional[HGESignal],
        location: Optional[CommanderLocation],
    ) -> Optional[dict]:
        """Calculate distance between signal and location."""
        if signal is None or location is None:
            return None

        distance = self.distance_calculator.calculate_distance(
            location.x,
            location.y,
            location.z,
            signal.x,
            signal.y,
            signal.z,
        )

        if distance is None:
            return None

        return {
            "distance_ly": distance,
            "formatted": self.distance_calculator.format_distance(distance),
        }

    def _format_notification_history(self) -> list:
        """Get formatted notification history."""
        try:
            history = self.notification_manager.get_notification_history(count=10)
            return [
                {
                    "system_name": notification.signal_system,
                    "distance_ly": notification.distance_ly,
                    "timestamp": notification.timestamp.isoformat(),
                    "channel": notification.channel,
                    "success": notification.success,
                    "error": notification.error,
                }
                for notification in history
            ]
        except Exception as e:
            self.logger.debug(f"Error getting notification history: {e}")
            return []

    def _get_notification_stats(self) -> dict:
        """Get notification statistics."""
        try:
            stats = self.notification_manager.get_stats()
            return {
                "total": stats.get("total", 0),
                "successful": stats.get("successful", 0),
                "failed": stats.get("failed", 0),
            }
        except Exception as e:
            self.logger.debug(f"Error getting notification stats: {e}")
            return {"total": 0, "successful": 0, "failed": 0}

    def get_signal_history(self, limit: int = 50) -> list:
        """Get the history of detected HGE signals.
        
        Args:
            limit: Maximum number of signals to return.
            
        Returns:
            List of formatted signal data, oldest first.
        """
        try:
            signals = list(self.signal_history)[-limit:]  # Get last N signals
            location = self.journal_parser.get_latest_location()
            
            result = []
            for signal in signals:
                signal_data = {
                    "system_name": signal.system_name,
                    "timestamp": signal.timestamp.isoformat(),
                    "age": signal.age_human_readable(),
                    "distance": 0,
                    "coordinates": {
                        "x": signal.x,
                        "y": signal.y,
                        "z": signal.z,
                    } if signal.x is not None else None,
                }
                
                # Calculate distance if both locations have coordinates
                if location and signal.x is not None and location.x is not None:
                    try:
                        distance = self.distance_calculator.calculate_distance(
                            location.x, location.y, location.z,
                            signal.x, signal.y, signal.z
                        )
                        if distance is not None:
                            signal_data["distance"] = round(distance, 2)
                    except Exception as e:
                        self.logger.debug(f"Error calculating distance: {e}")
                
                result.append(signal_data)
            
            return result
        except Exception as e:
            self.logger.debug(f"Error getting signal history: {e}")
            return []
