"""Core manager orchestrating all components."""

import logging
from pathlib import Path
from typing import Optional

from src.config.settings import get_settings
from src.distance import DistanceCalculator
from src.distance.coordinates import CoordinateDatabase
from src.eddn import EDDNMonitor, HGESignal
from src.journal import CommanderLocation, JournalParser


class HGENotifierManager:
    """Core manager orchestrating EDDN monitoring and location tracking."""

    def __init__(self) -> None:
        """Initialize the HGE Notifier Manager."""
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)
        
        # Initialize coordinate database
        data_path = self.settings.project_root / "data"
        self.coord_db = CoordinateDatabase(db_path=data_path)
        
        # Initialize EDDN monitor with callback
        self.eddn_monitor = EDDNMonitor(
            mock_mode=self.settings.eddn_mock_mode,
            callback=self._on_new_hge_signal,
        )
        
        # Initialize journal parser with callback
        self.journal_parser = JournalParser(
            journal_path=self.settings.journal_path,
            callback=self._on_location_change,
        )
        
        self.distance_calculator = DistanceCalculator()

        self._initialized = False

    def _on_new_hge_signal(self, signal: HGESignal) -> None:
        """Callback when new HGE signal is detected."""
        self.logger.info(f"New HGE signal in {signal.system_name}")

    def _on_location_change(self, location: CommanderLocation) -> None:
        """Callback when commander location changes."""
        self.logger.info(f"Location changed to {location.system_name}")

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
        Get current status including HGE signal, location, and distance.

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

        Args:
            location: Commander location

        Returns:
            Location with coordinates filled in if possible
        """
        if location is None or (location.x is not None and location.y is not None and location.z is not None):
            return location

        try:
            coords = self.coord_db.get_coordinates(location.system_name)
            if coords:
                location.x, location.y, location.z = coords
        except Exception as e:
            self.logger.debug(f"Error fetching coordinates for {location.system_name}: {e}")

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
