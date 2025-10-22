"""Tests for journal parsing."""

from datetime import datetime
import pytest
import tempfile
import json
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.journal import CommanderLocation, JournalParser


class TestCommanderLocation:
    """Test CommanderLocation dataclass."""

    def test_location_creation(self) -> None:
        """Test creating a commander location."""
        location = CommanderLocation(
            system_name="Sol",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0,
        )
        assert location.system_name == "Sol"
        assert location.x == 0.0


class TestJournalParser:
    """Test journal parsing functionality."""

    def test_journal_parser_mock_mode(self) -> None:
        """Test journal parser in mock mode (no journal path)."""
        parser = JournalParser(journal_path=None)
        parser.start()
        
        location = parser.get_latest_location()
        assert location is not None
        assert location.system_name == "Sol"
        assert location.x == 0.0
        assert location.y == 0.0
        assert location.z == 0.0

    def test_journal_parser_latest_location(self) -> None:
        """Test getting latest location."""
        parser = JournalParser(journal_path=None)
        parser.start()
        
        location = parser.get_latest_location()
        assert location is not None
        assert isinstance(location, CommanderLocation)


# ============================================================================
# PHASE 3 MEDIUM: JOURNAL FILE I/O EDGE CASES
# ============================================================================


class TestJournalFileIOEdgeCases:
    """Test file I/O edge cases for journal parser."""

    def test_parse_journal_file_missing_file(self) -> None:
        """Test parsing a journal file that doesn't exist."""
        parser = JournalParser(journal_path=None)
        parser.start()
        
        # Should not raise, just return silently
        parser._parse_journal_file(Path("/nonexistent/path/Journal.01.log"))
        
        parser.stop()

    def test_scan_latest_journal_no_files(self) -> None:
        """Test scanning journal directory with no journal files."""
        tmpdir = tempfile.mkdtemp()
        try:
            parser = JournalParser(journal_path=Path(tmpdir))
            parser.start()
            
            # Should fall back to mock location
            location = parser.get_latest_location()
            assert location is not None
            assert location.system_name == "Sol"
            
            parser.stop()
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_scan_latest_journal_directory_not_exists(self) -> None:
        """Test scanning when journal directory doesn't exist."""
        parser = JournalParser(journal_path=Path("/nonexistent/journal/path"))
        parser.start()
        
        # Should fall back to mock location
        location = parser.get_latest_location()
        assert location is not None
        assert location.system_name == "Sol"
        
        parser.stop()

    def test_parse_corrupted_json_entry(self) -> None:
        """Test parsing journal file with corrupted JSON lines."""
        tmpdir = tempfile.mkdtemp()
        try:
            journal_file = Path(tmpdir) / "Journal.01.log"
            
            # Write mixed valid and corrupted JSON
            with open(journal_file, "w", encoding="utf-8") as f:
                f.write('{"event": "Fileheader"}\n')
                f.write('CORRUPTED JSON LINE\n')
                f.write('{"event": "Location", "StarSystem": "Sol", "timestamp": "2025-10-22T10:30:45Z", "StarPos": [0.0, 0.0, 0.0]}\n')
            
            parser = JournalParser(journal_path=Path(tmpdir))
            parser.start()
            
            location = parser.get_latest_location()
            assert location is not None
            assert location.system_name == "Sol"
            
            parser.stop()
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_parse_empty_journal_file(self) -> None:
        """Test parsing an empty journal file."""
        tmpdir = tempfile.mkdtemp()
        try:
            journal_file = Path(tmpdir) / "Journal.01.log"
            journal_file.touch()  # Create empty file
            
            parser = JournalParser(journal_path=Path(tmpdir))
            parser.start()
            
            # Empty file means no location found, stays None until one is found
            location = parser.get_latest_location()
            # Location may be None or mock depending on internal logic
            assert location is None or location.system_name == "Sol"
            
            parser.stop()
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_parse_journal_with_no_location_events(self) -> None:
        """Test parsing journal with no location-related events."""
        tmpdir = tempfile.mkdtemp()
        try:
            journal_file = Path(tmpdir) / "Journal.01.log"
            
            with open(journal_file, "w", encoding="utf-8") as f:
                f.write('{"event": "Fileheader"}\n')
                f.write('{"event": "StartUp", "Commander": "TestCmdr"}\n')
                f.write('{"event": "OtherEvent", "data": "value"}\n')
            
            parser = JournalParser(journal_path=Path(tmpdir))
            parser.start()
            
            # No location event found, location stays None or mock
            location = parser.get_latest_location()
            assert location is None or location.system_name == "Sol"
            
            parser.stop()
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


# ============================================================================
# PHASE 3 MEDIUM: JOURNAL COORDINATE EXTRACTION EDGE CASES
# ============================================================================


class TestJournalCoordinateExtraction:
    """Test coordinate extraction and location handling edge cases."""

    def test_handle_location_event_missing_coordinates(self) -> None:
        """Test Location event with missing StarPos."""
        parser = JournalParser(journal_path=None)
        parser.start()
        
        entry = {
            "event": "Location",
            "StarSystem": "Alpha Centauri",
            "timestamp": "2025-10-22T10:30:45Z",
            # StarPos missing
        }
        
        parser._handle_location_event(entry)
        
        location = parser.get_latest_location()
        assert location is not None
        assert location.system_name == "Alpha Centauri"
        assert location.x is None
        assert location.y is None
        assert location.z is None
        
        parser.stop()

    def test_handle_location_event_partial_coordinates(self) -> None:
        """Test Location event with partial coordinates."""
        parser = JournalParser(journal_path=None)
        parser.start()
        
        entry = {
            "event": "Location",
            "StarSystem": "Betelgeuse",
            "timestamp": "2025-10-22T10:30:45Z",
            "StarPos": [10.5, 20.3],  # Only 2 coordinates
        }
        
        parser._handle_location_event(entry)
        
        location = parser.get_latest_location()
        assert location is not None
        assert location.x == 10.5
        assert location.y == 20.3
        assert location.z is None
        
        parser.stop()

    def test_handle_location_event_empty_starpos(self) -> None:
        """Test Location event with empty StarPos."""
        parser = JournalParser(journal_path=None)
        parser.start()
        
        entry = {
            "event": "Location",
            "StarSystem": "Sirius",
            "timestamp": "2025-10-22T10:30:45Z",
            "StarPos": [],
        }
        
        parser._handle_location_event(entry)
        
        location = parser.get_latest_location()
        assert location is not None
        assert location.system_name == "Sirius"
        assert location.x is None
        assert location.y is None
        assert location.z is None
        
        parser.stop()

    def test_handle_fsd_jump_event_coordinates(self) -> None:
        """Test FSDJump event with coordinates."""
        parser = JournalParser(journal_path=None)
        parser.start()
        
        entry = {
            "event": "FSDJump",
            "StarSystem": "Rigel",
            "timestamp": "2025-10-22T11:00:00Z",
            "StarPos": [5.5, 10.2, 15.8],
        }
        
        parser._handle_fsd_jump_event(entry)
        
        location = parser.get_latest_location()
        assert location is not None
        assert location.system_name == "Rigel"
        assert location.x == 5.5
        assert location.y == 10.2
        assert location.z == 15.8
        
        parser.stop()

    def test_handle_location_event_missing_system_name(self) -> None:
        """Test Location event with missing StarSystem."""
        parser = JournalParser(journal_path=None)
        parser.start()
        
        entry = {
            "event": "Location",
            # StarSystem missing
            "timestamp": "2025-10-22T10:30:45Z",
            "StarPos": [1.0, 2.0, 3.0],
        }
        
        parser._handle_location_event(entry)
        
        location = parser.get_latest_location()
        assert location is not None
        assert location.system_name == "Unknown"  # Default fallback
        
        parser.stop()

    def test_parse_timestamp_valid_format(self) -> None:
        """Test timestamp parsing with valid format."""
        result = JournalParser._parse_timestamp("2025-10-22T10:30:45Z")
        assert result is not None
        assert result.year == 2025
        assert result.month == 10
        assert result.day == 22

    def test_parse_timestamp_invalid_format(self) -> None:
        """Test timestamp parsing with invalid format."""
        result = JournalParser._parse_timestamp("invalid-timestamp")
        assert result is not None
        # Should return current time as fallback
        assert isinstance(result, datetime)

    def test_parse_timestamp_empty_string(self) -> None:
        """Test timestamp parsing with empty string."""
        result = JournalParser._parse_timestamp("")
        assert result is not None
        assert isinstance(result, datetime)

    def test_parse_timestamp_none(self) -> None:
        """Test timestamp parsing with None."""
        result = JournalParser._parse_timestamp(None)  # type: ignore
        assert result is not None
        assert isinstance(result, datetime)

    def test_get_latest_location_before_start(self) -> None:
        """Test getting location before parser started."""
        parser = JournalParser(journal_path=None)
        # Don't call start()
        
        location = parser.get_latest_location()
        assert location is None

    def test_location_callback_on_update(self) -> None:
        """Test callback is triggered on location update."""
        callback_mock = Mock()
        parser = JournalParser(journal_path=None, callback=callback_mock)
        parser.start()
        
        entry = {
            "event": "Location",
            "StarSystem": "Vega",
            "timestamp": "2025-10-22T12:00:00Z",
            "StarPos": [3.5, 4.5, 5.5],
        }
        
        parser._handle_location_event(entry)
        
        # Callback should have been called
        callback_mock.assert_called_once()
        called_location = callback_mock.call_args[0][0]
        assert called_location.system_name == "Vega"
        
        parser.stop()

    def test_multiple_location_events(self) -> None:
        """Test processing multiple location events."""
        parser = JournalParser(journal_path=None)
        parser.start()
        
        # First location
        entry1 = {
            "event": "Location",
            "StarSystem": "Polaris",
            "timestamp": "2025-10-22T10:00:00Z",
            "StarPos": [1.0, 1.0, 1.0],
        }
        parser._handle_location_event(entry1)
        loc1 = parser.get_latest_location()
        assert loc1.system_name == "Polaris"
        
        # Second location (should replace)
        entry2 = {
            "event": "FSDJump",
            "StarSystem": "Altair",
            "timestamp": "2025-10-22T11:00:00Z",
            "StarPos": [2.0, 2.0, 2.0],
        }
        parser._handle_fsd_jump_event(entry2)
        loc2 = parser.get_latest_location()
        assert loc2.system_name == "Altair"
        
        parser.stop()

    def test_journal_parser_stop_already_stopped(self) -> None:
        """Test stopping parser that's already stopped."""
        parser = JournalParser(journal_path=None)
        # Don't start it
        
        # Should not raise
        parser.stop()

    def test_journal_parser_start_already_running(self) -> None:
        """Test starting parser that's already running."""
        parser = JournalParser(journal_path=None)
        parser.start()
        
        # Should log warning but not raise
        parser.start()
        
        parser.stop()

    def test_file_position_tracking(self) -> None:
        """Test that file positions are tracked for partial reads."""
        tmpdir = tempfile.mkdtemp()
        try:
            journal_file = Path(tmpdir) / "Journal.01.log"
            
            with open(journal_file, "w", encoding="utf-8") as f:
                f.write('{"event": "Location", "StarSystem": "First", "timestamp": "2025-10-22T10:00:00Z", "StarPos": [1.0, 1.0, 1.0]}\n')
            
            parser = JournalParser(journal_path=Path(tmpdir))
            parser.start()
            
            # First parse should read from beginning
            assert journal_file in parser._file_positions
            first_pos = parser._file_positions[journal_file]
            assert first_pos > 0
            
            parser.stop()
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_journal_parser_with_large_coordinate_values(self) -> None:
        """Test handling very large coordinate values."""
        parser = JournalParser(journal_path=None)
        parser.start()
        
        entry = {
            "event": "Location",
            "StarSystem": "Far Away",
            "timestamp": "2025-10-22T10:30:45Z",
            "StarPos": [99999.99, 88888.88, 77777.77],
        }
        
        parser._handle_location_event(entry)
        
        location = parser.get_latest_location()
        assert location.x == 99999.99
        assert location.y == 88888.88
        assert location.z == 77777.77
        
        parser.stop()

    def test_journal_parser_with_negative_coordinates(self) -> None:
        """Test handling negative coordinate values."""
        parser = JournalParser(journal_path=None)
        parser.start()
        
        entry = {
            "event": "Location",
            "StarSystem": "Negative Space",
            "timestamp": "2025-10-22T10:30:45Z",
            "StarPos": [-10.5, -20.3, -30.1],
        }
        
        parser._handle_location_event(entry)
        
        location = parser.get_latest_location()
        assert location.x == -10.5
        assert location.y == -20.3
        assert location.z == -30.1
        
        parser.stop()

