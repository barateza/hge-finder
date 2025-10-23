"""EDDN module - High Grade Emission data ingestion."""

import json
import logging
import threading
import time
import zmq
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Callable


logger = logging.getLogger(__name__)


@dataclass
class HGESignal:
    """Represents a High Grade Emission signal from EDDN."""

    system_name: str
    """Name of the system where HGE was detected."""
    
    timestamp: datetime
    """When the signal was detected."""
    
    x: Optional[float] = None
    """X coordinate of the system."""
    
    y: Optional[float] = None
    """Y coordinate of the system."""
    
    z: Optional[float] = None
    """Z coordinate of the system."""

    def age_seconds(self) -> int:
        """Get age of signal in seconds."""
        return int((datetime.utcnow() - self.timestamp).total_seconds())

    def age_human_readable(self) -> str:
        """Get human-readable age of signal."""
        age = self.age_seconds()
        
        if age < 60:
            return f"{age}s ago"
        elif age < 3600:
            return f"{age // 60}m ago"
        elif age < 86400:
            return f"{age // 3600}h ago"
        else:
            return f"{age // 86400}d ago"


class EDDNMonitor:
    """Monitor Elite Dangerous Data Network for HGE signals."""

    # EDDN connection settings
    EDDN_ENDPOINT = "tcp://eddn.edcd.io:9500"
    EDDN_TIMEOUT = 5000  # milliseconds
    MAX_RECONNECT_ATTEMPTS = 5
    RECONNECT_DELAY = 5  # seconds

    def __init__(self, mock_mode: bool = True, callback: Optional[Callable] = None) -> None:
        """
        Initialize EDDN monitor.

        Args:
            mock_mode: If True, use mock data. If False, connect to real EDDN.
            callback: Optional callback function to call when new signal is detected.
        """
        self.mock_mode = mock_mode
        self.callback = callback
        self.latest_signal: Optional[HGESignal] = None
        self.is_running = False
        self.zmq_context: Optional[zmq.Context] = None
        self.zmq_socket: Optional[zmq.Socket] = None
        self._monitor_thread: Optional[threading.Thread] = None
        self._reconnect_count = 0

    def start(self) -> None:
        """Start monitoring EDDN."""
        if self.is_running:
            logger.warning("EDDN monitor already running")
            return

        self.is_running = True
        
        if self.mock_mode:
            logger.info("Starting EDDN monitor in mock mode")
            self._init_mock_data()
        else:
            logger.info("Starting EDDN monitor with real EDDN connection")
            self._monitor_thread = threading.Thread(
                target=self._connect_and_monitor,
                daemon=True,
            )
            self._monitor_thread.start()

    def stop(self) -> None:
        """Stop monitoring EDDN."""
        if not self.is_running:
            return

        logger.info("Stopping EDDN monitor")
        self.is_running = False
        
        self._close_zmq()
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)

    def get_latest_signal(self) -> Optional[HGESignal]:
        """Get the latest HGE signal detected."""
        return self.latest_signal

    def _init_mock_data(self) -> None:
        """Initialize with mock data for testing."""
        self.latest_signal = HGESignal(
            system_name="Shinrarta Dezhra",
            timestamp=datetime.utcnow(),
            x=55.71905517578125,
            y=-49.50000381469727,
            z=17.399999618530273,
        )

    def _connect_and_monitor(self) -> None:
        """Connect to real EDDN and monitor for signals."""
        while self.is_running:
            try:
                self._connect_to_eddn()
                self._monitor_eddn_stream()
            except Exception as e:
                logger.error(f"Error in EDDN monitoring: {e}")
                self._handle_reconnect()

    def _connect_to_eddn(self) -> None:
        """Establish ZMQ connection to EDDN."""
        logger.info(f"Connecting to EDDN at {self.EDDN_ENDPOINT}")
        
        try:
            self.zmq_context = zmq.Context()
            self.zmq_socket = self.zmq_context.socket(zmq.SUB)
            
            assert self.zmq_socket is not None, "Failed to create ZMQ socket"
            
            # Subscribe to all messages (empty subscribe = all)
            self.zmq_socket.setsockopt(zmq.SUBSCRIBE, b"")
            
            # Set socket options
            self.zmq_socket.setsockopt(zmq.RCVTIMEO, self.EDDN_TIMEOUT)
            
            # Connect
            self.zmq_socket.connect(self.EDDN_ENDPOINT)
            
            logger.info("Successfully connected to EDDN")
            self._reconnect_count = 0  # Reset reconnect counter
            
        except Exception as e:
            logger.error(f"Failed to connect to EDDN: {e}")
            self._close_zmq()
            raise

    def _monitor_eddn_stream(self) -> None:
        """Monitor EDDN stream for messages."""
        while self.is_running:
            try:
                assert self.zmq_socket is not None, "ZMQ socket not initialized"
                message = self.zmq_socket.recv_multipart()
                self._process_eddn_message(message)
            except zmq.error.Again:
                # Timeout - no message received, that's ok
                continue
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                raise

    def _process_eddn_message(self, message: list) -> None:
        """
        Process received EDDN message.

        EDDN messages are multipart:
        [0] = header (not used)
        [1] = JSON payload
        """
        try:
            if len(message) < 2:
                return

            # Decompress and parse JSON
            json_str = message[1]
            data = json.loads(json_str)

            # Check if this is a HighGradeEmission message
            if self._is_hge_message(data):
                signal = self._parse_hge_signal(data)
                if signal:
                    self.latest_signal = signal
                    logger.info(f"New HGE signal: {signal.system_name}")
                    
                    if self.callback:
                        self.callback(signal)

        except json.JSONDecodeError as e:
            logger.debug(f"Failed to parse JSON: {e}")
        except Exception as e:
            logger.error(f"Error processing EDDN message: {e}")

    @staticmethod
    def _is_hge_message(data: dict) -> bool:
        """
        Check if message is a HighGradeEmission event.

        Args:
            data: Parsed EDDN message

        Returns:
            True if message contains HGE data
        """
        # Check various message types that might contain HGE data
        message_type = data.get("$schemaRef", "")
        
        # HGE signals typically come from:
        # - Codex entries (schema: .../codex/1)
        # - USS (Unidentified Signal Source) discoveries (schema: .../uss/1 or .../journal/1/uss)
        
        if "uss" in message_type.lower() or "codex" in message_type.lower():
            # Additional filtering: ensure it's actually a HIGH GRADE emission
            # Check for HGE identifiers in the message data
            
            # USS messages have USSType field
            uss_type = data.get("USSType", "").lower()
            if "high" in uss_type and "grade" in uss_type:
                return True
            
            # Codex entries might have name or description field
            name = data.get("Name", "").lower() or data.get("name", "").lower()
            description = data.get("Description", "").lower() or data.get("description", "").lower()
            
            if ("high grade emission" in name or 
                "high grade emission" in description or
                ("high" in name and "grade" in name) or
                ("high" in description and "grade" in description)):
                return True
            
            # Journal-based USS events (event type USSDrop with HGE threat level)
            # These should have EventType: 'USSDrop' and USSType containing 'High grade emissions'
            event_type = data.get("Event") or data.get("event")
            if event_type == "USSDrop":
                uss_type_journal = data.get("USSType", "").lower()
                if "high" in uss_type_journal and "grade" in uss_type_journal:
                    return True
        
        return False

    @staticmethod
    def _parse_hge_signal(data: dict) -> Optional[HGESignal]:
        """
        Parse HGE signal from EDDN message.

        Args:
            data: Parsed EDDN message

        Returns:
            HGESignal object or None if parsing fails
        """
        try:
            # Extract system name
            system_name = data.get("StarSystem")
            if not system_name:
                return None

            # Extract timestamp
            timestamp_str = data.get("timestamp")
            if not timestamp_str:
                timestamp = datetime.utcnow()
            else:
                timestamp = datetime.fromisoformat(
                    timestamp_str.replace("Z", "+00:00")
                )

            # Extract coordinates
            star_pos = data.get("StarPos")
            x = star_pos[0] if star_pos and len(star_pos) > 0 else None
            y = star_pos[1] if star_pos and len(star_pos) > 1 else None
            z = star_pos[2] if star_pos and len(star_pos) > 2 else None

            signal = HGESignal(
                system_name=system_name,
                timestamp=timestamp,
                x=x,
                y=y,
                z=z,
            )
            
            # Log the extracted signal for debugging
            logger.debug(
                f"Parsed HGE signal: {system_name} at {timestamp.isoformat()} "
                f"coords: ({x}, {y}, {z})"
            )

            return signal

        except (KeyError, IndexError, ValueError) as e:
            logger.debug(f"Failed to parse HGE signal: {e}")
            return None

    def _handle_reconnect(self) -> None:
        """Handle reconnection with exponential backoff."""
        self._close_zmq()
        
        if not self.is_running:
            return

        self._reconnect_count += 1
        
        if self._reconnect_count > self.MAX_RECONNECT_ATTEMPTS:
            logger.error(
                f"Max reconnection attempts ({self.MAX_RECONNECT_ATTEMPTS}) "
                "reached. Switching to mock mode."
            )
            self.mock_mode = True
            self._init_mock_data()
            self._reconnect_count = 0
            return

        # Exponential backoff
        delay = min(self.RECONNECT_DELAY * (2 ** (self._reconnect_count - 1)), 300)
        logger.info(f"Reconnecting to EDDN in {delay}s (attempt {self._reconnect_count})")
        time.sleep(delay)

    def _close_zmq(self) -> None:
        """Close ZMQ socket and context."""
        try:
            if self.zmq_socket:
                self.zmq_socket.close(linger=0)
                self.zmq_socket = None
        except Exception as e:
            logger.error(f"Error closing ZMQ socket: {e}")

        try:
            if self.zmq_context:
                self.zmq_context.term()
                self.zmq_context = None
        except Exception as e:
            logger.error(f"Error terminating ZMQ context: {e}")

