"""Journal module - Elite Dangerous journal parsing."""

import json
import logging
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from watchdog.observers import Observer


logger = logging.getLogger(__name__)


@dataclass
class CommanderLocation:
    """Represents the commander's current location."""

    system_name: str
    """Name of the current system."""
    
    timestamp: datetime
    """When this location was last updated."""
    
    x: Optional[float] = None
    """X coordinate of the system."""
    
    y: Optional[float] = None
    """Y coordinate of the system."""
    
    z: Optional[float] = None
    """Z coordinate of the system."""


class JournalFileHandler(FileSystemEventHandler):
    """Handle journal file events."""

    def __init__(self, parser: "JournalParser") -> None:
        """
        Initialize journal file handler.

        Args:
            parser: JournalParser instance
        """
        self.parser = parser

    def on_modified(self, event: FileModifiedEvent) -> None:
        """Handle file modification events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        
        # Only process journal files
        if not file_path.name.startswith("Journal.") or not file_path.suffix == ".log":
            return

        self.parser._parse_journal_file(file_path, from_end=True)


class JournalParser:
    """Parse Elite Dangerous journal files."""

    def __init__(
        self,
        journal_path: Optional[Path] = None,
        callback: Optional[Callable] = None,
    ) -> None:
        """
        Initialize journal parser.

        Args:
            journal_path: Path to the journal directory.
            callback: Optional callback function to call when location changes.
        """
        self.journal_path = journal_path
        self.callback = callback
        self.latest_location: Optional[CommanderLocation] = None
        self.is_running = False
        self._observer = None  # type: ignore
        self._last_journal_file: Optional[Path] = None
        self._file_positions: dict = {}  # Track file reading positions

    def start(self) -> None:
        """Start monitoring journal files."""
        if self.is_running:
            logger.warning("Journal parser already running")
            return

        self.is_running = True

        if self.journal_path is None or not self.journal_path.exists():
            logger.info("Journal path not configured or not found, using mock location")
            self._init_mock_location()
        else:
            logger.info(f"Starting journal parser watching {self.journal_path}")
            
            # Parse existing journal first
            self._scan_latest_journal()
            
            # Start watching for changes
            self._start_watching()

    def stop(self) -> None:
        """Stop monitoring journal files."""
        if not self.is_running:
            return

        logger.info("Stopping journal parser")
        self.is_running = False

        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None

    def get_latest_location(self) -> Optional[CommanderLocation]:
        """Get the commander's latest known location."""
        return self.latest_location

    def _init_mock_location(self) -> None:
        """Initialize with mock location for testing."""
        self.latest_location = CommanderLocation(
            system_name="Sol",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0,
        )

    def _start_watching(self) -> None:
        """Start watching journal directory for changes."""
        try:
            self._observer = Observer()
            handler = JournalFileHandler(self)
            self._observer.schedule(handler, str(self.journal_path), recursive=False)
            self._observer.start()
            logger.info("Journal directory watcher started")
        except Exception as e:
            logger.error(f"Failed to start journal watcher: {e}")
            self._observer = None

    def _scan_latest_journal(self) -> None:
        """Scan the latest journal file for location info."""
        if not self.journal_path:
            return

        try:
            # Find the most recent journal file
            journal_files = sorted(
                self.journal_path.glob("Journal.*.log"),
                reverse=True,
            )

            if not journal_files:
                logger.warning("No journal files found")
                self._init_mock_location()
                return

            # Parse the latest journal file
            self._parse_journal_file(journal_files[0])
            self._last_journal_file = journal_files[0]

        except Exception as e:
            logger.error(f"Error scanning journal directory: {e}")
            self._init_mock_location()

    def _parse_journal_file(
        self,
        file_path: Path,
        from_end: bool = False,
    ) -> None:
        """
        Parse a journal file for location information.

        Args:
            file_path: Path to the journal file.
            from_end: If True, only read new lines (for live monitoring).
        """
        try:
            if not file_path.exists():
                return

            file_size = file_path.stat().st_size

            # Determine where to start reading
            if from_end and file_path in self._file_positions:
                start_pos = self._file_positions[file_path]
            else:
                start_pos = 0

            with open(file_path, "r", encoding="utf-8") as f:
                # Seek to last known position if watching for changes
                if start_pos > 0:
                    f.seek(start_pos)

                for line in f:
                    try:
                        entry = json.loads(line)
                        self._process_journal_entry(entry)
                    except json.JSONDecodeError:
                        continue

                # Remember position for next read
                self._file_positions[file_path] = f.tell()

        except (IOError, OSError) as e:
            logger.error(f"Error reading journal file {file_path}: {e}")

    def _process_journal_entry(self, entry: dict) -> None:
        """
        Process a journal entry.

        Args:
            entry: Parsed journal entry dictionary
        """
        event_type = entry.get("event")

        if event_type == "Location":
            self._handle_location_event(entry)
        elif event_type == "FSDJump":
            self._handle_fsd_jump_event(entry)
        elif event_type == "SupercruiseExit":
            self._handle_location_event(entry)

    def _handle_location_event(self, entry: dict) -> None:
        """Handle Location event from journal."""
        try:
            system_name = entry.get("StarSystem", "Unknown")
            timestamp_str = entry.get("timestamp", "")
            star_pos = entry.get("StarPos", [None, None, None])

            timestamp = self._parse_timestamp(timestamp_str)

            new_location = CommanderLocation(
                system_name=system_name,
                timestamp=timestamp,
                x=star_pos[0] if len(star_pos) > 0 else None,
                y=star_pos[1] if len(star_pos) > 1 else None,
                z=star_pos[2] if len(star_pos) > 2 else None,
            )

            self.latest_location = new_location
            logger.debug(f"Location updated: {system_name}")

            if self.callback:
                self.callback(new_location)

        except Exception as e:
            logger.error(f"Error processing Location event: {e}")

    def _handle_fsd_jump_event(self, entry: dict) -> None:
        """Handle FSDJump event from journal."""
        try:
            system_name = entry.get("StarSystem", "Unknown")
            timestamp_str = entry.get("timestamp", "")
            star_pos = entry.get("StarPos", [None, None, None])

            timestamp = self._parse_timestamp(timestamp_str)

            new_location = CommanderLocation(
                system_name=system_name,
                timestamp=timestamp,
                x=star_pos[0] if len(star_pos) > 0 else None,
                y=star_pos[1] if len(star_pos) > 1 else None,
                z=star_pos[2] if len(star_pos) > 2 else None,
            )

            self.latest_location = new_location
            logger.debug(f"FSD Jump detected: {system_name}")

            if self.callback:
                self.callback(new_location)

        except Exception as e:
            logger.error(f"Error processing FSDJump event: {e}")

    @staticmethod
    def _parse_timestamp(timestamp_str: str) -> datetime:
        """
        Parse Elite Dangerous timestamp format.

        Args:
            timestamp_str: Timestamp string in format "2025-10-22T10:30:45Z"

        Returns:
            Parsed datetime object
        """
        try:
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            logger.debug(f"Could not parse timestamp: {timestamp_str}")
            return datetime.utcnow()

