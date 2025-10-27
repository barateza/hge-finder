"""EDDN module - High Grade Emission data ingestion."""

import json
import logging
import threading
import time
import zmq
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Callable

from src.system_info import SystemInfoLookup

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
    
    allegiance: Optional[str] = None
    """System allegiance (Federation, Empire, Alliance, Independent)."""
    
    government: Optional[str] = None
    """System government type."""
    
    population: Optional[int] = None
    """System population."""
    
    state: Optional[str] = None
    """Current system faction state (War, Civil Unrest, Outbreak, Boom, etc)."""

    def age_seconds(self) -> int:
        """Get age of signal in seconds."""
        now = datetime.now(timezone.utc)
        ts = self.timestamp
        
        # Handle both naive and timezone-aware datetimes
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        
        return int((now - ts).total_seconds())

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
    """Monitor Elite Dangerous Data Network for HGE signals.
    
    HGE signals reach EDDN via:
    1. FSSSignalDiscovered schema events when players discover USS signals via FSS
    2. Specifically: USS with USSType = "$USS_Type_VeryValuableSalvage;"
    
    This allows tracking HGE across the galaxy from other players' discoveries.
    
    Note: Local HGE drops (from your own journal) are detected separately via
    the JournalParser which listens for USSDrop/SupercruiseDestinationDrop events.
    """

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
        
        # Close ZMQ first (signals thread to stop)
        self._close_zmq()
        
        # Then wait for thread to finish
        if self._monitor_thread and self._monitor_thread.is_alive():
            try:
                self._monitor_thread.join(timeout=5)
            except Exception as e:
                logger.warning(f"Error joining monitor thread: {e}")

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
        logger.info("📊 EDDN monitoring thread started")
        while self.is_running:
            try:
                self._connect_to_eddn()
                self._monitor_eddn_stream()
            except Exception as e:
                logger.error(f"❌ Error in EDDN monitoring: {e}", exc_info=True)
                self._handle_reconnect()

    def _connect_to_eddn(self) -> None:
        """Establish ZMQ connection to EDDN."""
        logger.info(f"🔌 Connecting to EDDN at {self.EDDN_ENDPOINT}")
        
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
            
            logger.info(f"✅ Successfully connected to EDDN at {self.EDDN_ENDPOINT}")
            logger.info("📡 Starting to receive EDDN stream... (first message may take a few seconds)")
            self._reconnect_count = 0  # Reset reconnect counter
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to EDDN: {e}")
            self._close_zmq()
            raise

    def _monitor_eddn_stream(self) -> None:
        """Monitor EDDN stream for messages."""
        message_count = 0
        hge_count = 0
        logged_message_types = set()
        timeout_count = 0
        first_message = True
        
        while self.is_running:
            try:
                assert self.zmq_socket is not None, "ZMQ socket not initialized"
                message = self.zmq_socket.recv_multipart()
                timeout_count = 0  # Reset timeout counter on success
                message_count += 1
                
                # Log the FIRST message we receive to verify schema
                if first_message:
                    first_message = False
                    logger.info(f"📨 First EDDN message received! (message size: {len(message)} parts)")
                
                # Log sample of message types (first 10 unique types)
                if len(message) >= 2:
                    try:
                        data = json.loads(message[1])
                        schema_ref = data.get("$schemaRef", "unknown")
                        if schema_ref not in logged_message_types and len(logged_message_types) < 10:
                            logged_message_types.add(schema_ref)
                            logger.info(f"[EDDN Stream] Sample message type #{len(logged_message_types)}: {schema_ref}")
                        
                        # Periodic summary logging
                        if message_count % 100 == 0:
                            logger.info(f"[EDDN Stream] Received {message_count} messages, {hge_count} HGE signals detected")
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON from EDDN: {e}")
                
                # Process and track HGE signals
                result = self._process_eddn_message(message)
                if result:  # We'll return True if HGE was detected
                    hge_count += 1
                    
            except zmq.error.Again:
                # Timeout - no message received in 5 seconds
                timeout_count += 1
                if timeout_count == 1:
                    logger.warning(f"⏱️ EDDN stream timeout (no messages for 5s after connection)")
                if timeout_count % 60 == 0:  # Log every 300 seconds of timeouts
                    logger.warning(f"⏱️ EDDN stream still timing out (no messages for {timeout_count * 5}s). Received {message_count} total messages in this session.")
                continue
            except Exception as e:
                logger.error(f"❌ Error receiving message: {e}", exc_info=True)
                raise

    def _process_eddn_message(self, message: list) -> bool:
        """
        Process received EDDN message.

        EDDN messages are single-part, zlib-compressed JSON.
        
        Returns:
            True if HGE signal was detected and processed, False otherwise
        """
        try:
            if len(message) < 1:
                return False

            # Decompress the message
            try:
                import zlib
                decompressed = zlib.decompress(message[0])
                json_str = decompressed.decode('utf-8')
            except Exception as e:
                logger.debug(f"Failed to decompress message: {e}")
                return False
            
            # Parse JSON
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.debug(f"Failed to parse JSON: {e}")
                return False

            # Check if this is a HighGradeEmission message
            if self._is_hge_message(data):
                signal = self._parse_hge_signal(data)
                if signal:
                    self.latest_signal = signal
                    logger.info(f"🎯 New HGE signal detected: {signal.system_name}")
                    
                    if self.callback:
                        self.callback(signal)
                    return True
            return False

        except Exception as e:
            logger.error(f"Error processing EDDN message: {e}")
            return False

    @staticmethod
    def _is_hge_message(data: dict) -> bool:
        """
        Check if message contains a HighGradeEmission signal.

        Supports multiple EDDN message formats:

        1. EDDN FSS Signal Discovered:
           {
               "$schemaRef": "https://eddn.edcd.io/schemas/fsssignaldiscovered/1",
               "message": {
                   "signals": [
                       {"USSType": "$USS_Type_VeryValuableSalvage;", ...},
                       ...
                   ],
                   ...
               }
           }

        2. EDDN USS schema (direct USS format):
           {
               "$schemaRef": "https://eddn.edcd.io/schemas/uss/1",
               "USSType": "High Grade Emissions",
               ...
           }

        3. EDDN Codex schema:
           {
               "$schemaRef": "https://eddn.edcd.io/schemas/codex/1",
               "Name": "High Grade Emission",
               "Description": "High Grade Emission Signal",
               ...
           }

        4. EDDN Journal USS format:
           {
               "$schemaRef": "https://eddn.edcd.io/schemas/journal/1/uss",
               "Event": "USSDrop",
               "USSType": "High grade emissions",
               ...
           }

        Args:
            data: Parsed EDDN message

        Returns:
            True if message contains HGE signal
        """
        try:
            schema_ref = data.get("$schemaRef", "").lower()
            
            # Format 1: FSS Signal Discovered
            if "fsssignaldiscovered" in schema_ref:
                message = data.get("message", {})
                if not isinstance(message, dict):
                    return False
                
                signals = message.get("signals", [])
                if not isinstance(signals, list):
                    return False
                
                for signal in signals:
                    uss_type = signal.get("USSType", "").lower()
                    if "veryvaluablesalvage" in uss_type:
                        logger.debug(f"HGE detected (FSS): {uss_type}")
                        return True
            
            # Format 2: Direct USS format or Journal USS format
            elif "uss" in schema_ref or "/uss" in schema_ref:
                uss_type = data.get("USSType", "").lower()
                if "high grade" in uss_type or "veryvaluablesalvage" in uss_type:
                    logger.debug(f"HGE detected (USS): {uss_type}")
                    return True
            
            # Format 3: Codex format
            elif "codex" in schema_ref:
                name = data.get("Name", "").lower()
                description = data.get("Description", "").lower()
                
                if "high grade emission" in name or "high grade emission" in description:
                    logger.debug(f"HGE detected (Codex): {name or description}")
                    return True
            
            return False
        except Exception as e:
            logger.debug(f"Error checking if HGE message: {e}")
            return False

    @staticmethod
    def _parse_hge_signal(data: dict) -> Optional[HGESignal]:
        """
        Parse HGE signal from EDDN message.

        Handles various message formats and gracefully falls back to None/defaults
        for missing optional fields.

        Args:
            data: Parsed EDDN message (must have passed _is_hge_message check)

        Returns:
            HGESignal object or None if parsing fails (missing required system name)
        """
        try:
            # Try to find system name - check multiple formats
            message = data.get("message", {})
            system_name = data.get("StarSystem") or message.get("StarSystem")
            
            if not system_name:
                return None

            # Extract timestamp with fallback to current time
            timestamp_str = data.get("timestamp") or message.get("timestamp")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(
                        timestamp_str.replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    # If timestamp is malformed, fail parsing
                    logger.debug(f"Failed to parse malformed timestamp: {timestamp_str}")
                    return None
            else:
                # If no timestamp provided, use current UTC time
                timestamp = datetime.now(timezone.utc)

            # Extract coordinates - handle partial or missing data gracefully
            star_pos = data.get("StarPos") or message.get("StarPos")
            x = None
            y = None
            z = None
            
            if star_pos and isinstance(star_pos, list):
                try:
                    x = float(star_pos[0]) if len(star_pos) > 0 else None
                except (ValueError, IndexError, TypeError):
                    x = None
                
                try:
                    y = float(star_pos[1]) if len(star_pos) > 1 else None
                except (ValueError, IndexError, TypeError):
                    y = None
                
                try:
                    z = float(star_pos[2]) if len(star_pos) > 2 else None
                except (ValueError, IndexError, TypeError):
                    z = None

            # Try to get system context from EDDN first
            allegiance = data.get("SystemAllegiance") or message.get("SystemAllegiance")
            government = data.get("SystemGovernment") or message.get("SystemGovernment")
            population = data.get("Population") or message.get("Population")
            state = None
            
            factions = data.get("Factions", []) or message.get("Factions", [])
            if factions and len(factions) > 0:
                state = factions[0].get("FactionState")
            
            # If missing, look up from EDSM
            if not allegiance or not state:
                try:
                    system_info = SystemInfoLookup.get_system_info(system_name)
                    if system_info:
                        allegiance = allegiance or system_info.get("allegiance")
                        government = government or system_info.get("government")
                        population = population or system_info.get("population")
                        state = state or system_info.get("state")
                except Exception as e:
                    logger.debug(f"Error looking up system info for {system_name}: {e}")

            signal = HGESignal(
                system_name=system_name,
                timestamp=timestamp,
                x=x,
                y=y,
                z=z,
                allegiance=allegiance,
                government=government,
                population=population,
                state=state,
            )
            
            logger.debug(
                f"Parsed HGE signal: {system_name} at {timestamp.isoformat()} "
                f"coords: ({x}, {y}, {z}) allegiance: {allegiance} state: {state}"
            )

            return signal

        except (KeyError, TypeError) as e:
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
        """Close ZMQ socket and context safely.
        
        This method handles both normal shutdown and crash scenarios.
        It's designed to be thread-safe even when called from multiple contexts.
        """
        # Close socket first (with short linger to prevent hangs)
        try:
            if self.zmq_socket:
                try:
                    self.zmq_socket.close(linger=0)
                except zmq.error.ZMQError as e:
                    logger.debug(f"ZMQ socket already closed or invalid: {e}")
                finally:
                    self.zmq_socket = None
        except Exception as e:
            logger.debug(f"Unexpected error closing ZMQ socket: {e}")

        # Then terminate context (with short timeout to prevent hangs)
        try:
            if self.zmq_context:
                try:
                    # Use term() instead of destroy() to allow graceful shutdown
                    # This will block until context is empty or timeout occurs
                    self.zmq_context.term()
                except (zmq.error.ZMQError, RuntimeError) as e:
                    logger.debug(f"ZMQ context already terminated or invalid: {e}")
                    # Force destruction if term fails
                    try:
                        self.zmq_context.destroy()
                    except Exception:
                        pass
                finally:
                    self.zmq_context = None
        except Exception as e:
            logger.debug(f"Unexpected error closing ZMQ context: {e}")

