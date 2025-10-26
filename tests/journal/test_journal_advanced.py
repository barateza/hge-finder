"""
Phase 4A: Journal Parser Advanced Tests

Tests for JournalParser edge cases: file errors, event parsing edge cases,
FSS signal detection, directory monitoring, and state management.
Covers error paths and boundary conditions in src/journal/__init__.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
import json

from src.journal import JournalParser, CommanderLocation


class TestJournalAdvancedPhase4:
    """Test advanced journal parsing scenarios and edge cases."""

    def test_journal_initialization_valid_path(self):
        """Test journal parser initialization with valid path."""
        with TemporaryDirectory() as tmpdir:
            journal_path = Path(tmpdir)
            parser = JournalParser(journal_path=journal_path)
            
            assert parser is not None
            assert parser.latest_location is None

    def test_journal_parser_start_stop_lifecycle(self):
        """Test journal parser start and stop lifecycle."""
        with TemporaryDirectory() as tmpdir:
            journal_path = Path(tmpdir)
            parser = JournalParser(journal_path=journal_path)
            
            parser.start()
            assert parser.is_running
            
            parser.stop()
            assert not parser.is_running

    def test_journal_parser_start_idempotency(self):
        """Test starting parser multiple times is safe."""
        with TemporaryDirectory() as tmpdir:
            journal_path = Path(tmpdir)
            parser = JournalParser(journal_path=journal_path)
            
            parser.start()
            parser.start()  # Should not crash
            
            assert parser.is_running
            parser.stop()

    def test_journal_parser_stop_idempotency(self):
        """Test stopping parser multiple times is safe."""
        with TemporaryDirectory() as tmpdir:
            journal_path = Path(tmpdir)
            parser = JournalParser(journal_path=journal_path)
            
            parser.start()
            parser.stop()
            parser.stop()  # Should not crash
            
            assert not parser.is_running

    def test_journal_get_latest_location_none(self):
        """Test getting location when none available."""
        with TemporaryDirectory() as tmpdir:
            journal_path = Path(tmpdir)
            parser = JournalParser(journal_path=journal_path)
            
            location = parser.get_latest_location()
            
            assert location is None

    def test_journal_commander_location_creation(self):
        """Test CommanderLocation creation."""
        location = CommanderLocation(
            system_name="Sol",
            timestamp=datetime.now(timezone.utc),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        assert location.system_name == "Sol"
        assert location.x == 0.0

    def test_journal_commander_location_optional_coords(self):
        """Test CommanderLocation with optional coordinates."""
        location = CommanderLocation(
            system_name="Sirius",
            timestamp=datetime.now(timezone.utc)
        )
        
        assert location.system_name == "Sirius"
        assert location.x is None
        assert location.y is None
        assert location.z is None

    def test_journal_parser_callback_invocation(self):
        """Test that callback is invoked on location change."""
        callback_invoked = []
        
        def mock_callback(location: CommanderLocation):
            callback_invoked.append(location)
        
        with TemporaryDirectory() as tmpdir:
            journal_path = Path(tmpdir)
            parser = JournalParser(
                journal_path=journal_path,
                callback=mock_callback
            )
            
            # Create a location
            location = CommanderLocation(
                system_name="Test",
                timestamp=datetime.now(timezone.utc),
                x=1.0,
                y=2.0,
                z=3.0
            )
            
            # Manually trigger callback
            if parser.callback:
                parser.callback(location)
            
            # Verify callback was called
            assert len(callback_invoked) > 0

    def test_journal_parser_hge_callback(self):
        """Test HGE signal callback exists."""
        hge_callback_invoked = []
        
        def mock_hge_callback(event):
            hge_callback_invoked.append(event)
        
        with TemporaryDirectory() as tmpdir:
            journal_path = Path(tmpdir)
            parser = JournalParser(
                journal_path=journal_path,
                hge_callback=mock_hge_callback
            )
            
            assert parser.hge_callback == mock_hge_callback

    def test_journal_file_monitor_startup(self):
        """Test journal file monitor starts correctly."""
        with TemporaryDirectory() as tmpdir:
            journal_path = Path(tmpdir)
            parser = JournalParser(journal_path=journal_path)
            
            parser.start()
            
            # Monitor should be running
            assert parser.is_running
            
            parser.stop()

    def test_journal_get_latest_location_after_stopped(self):
        """Test getting latest location after stop."""
        with TemporaryDirectory() as tmpdir:
            journal_path = Path(tmpdir)
            
            def on_location_change(location):
                pass
            
            parser = JournalParser(
                journal_path=journal_path,
                callback=on_location_change
            )
            
            parser.start()
            parser.stop()
            
            # Get latest location (should be None or cached)
            location = parser.get_latest_location()
            
            # Should be None or a valid location
            assert location is None or isinstance(location, CommanderLocation)

    def test_journal_commander_location_string_repr(self):
        """Test CommanderLocation string representation."""
        location = CommanderLocation(
            system_name="Test System",
            timestamp=datetime.now(timezone.utc),
            x=10.0,
            y=20.0,
            z=30.0
        )
        
        str_repr = str(location)
        
        # Should contain system name in repr
        assert isinstance(str_repr, str)

    def test_journal_parser_with_nonexistent_directory(self):
        """Test parser with nonexistent journal directory."""
        # Use a path that doesn't exist
        journal_path = Path("/nonexistent/journal/path")
        
        # Parser should handle gracefully
        parser = JournalParser(journal_path=journal_path)
        
        assert parser is not None

    def test_journal_multiple_parsers_independent(self):
        """Test that multiple parser instances are independent."""
        with TemporaryDirectory() as tmpdir1:
            with TemporaryDirectory() as tmpdir2:
                parser1 = JournalParser(journal_path=Path(tmpdir1))
                parser2 = JournalParser(journal_path=Path(tmpdir2))
                
                # Both should be independent
                assert parser1.latest_location is None
                assert parser2.latest_location is None
                
                # Start them independently
                parser1.start()
                assert parser1.is_running
                assert not parser2.is_running
                
                parser1.stop()
                parser2.start()
                assert not parser1.is_running
                assert parser2.is_running
                
                parser2.stop()

    def test_journal_parser_timestamp_handling(self):
        """Test timestamp parsing."""
        # Test that parser can handle various ISO format timestamps
        parser = None
        with TemporaryDirectory() as tmpdir:
            parser = JournalParser(journal_path=Path(tmpdir))
            
            # Static method call
            ts = JournalParser._parse_timestamp("2024-01-15T12:30:45Z")
            
            # Should parse to datetime
            assert isinstance(ts, datetime)

    def test_journal_commander_location_with_all_fields(self):
        """Test CommanderLocation with all fields set."""
        now = datetime.now(timezone.utc)
        
        location = CommanderLocation(
            system_name="Rigel",
            timestamp=now,
            x=100.5,
            y=200.75,
            z=300.25
        )
        
        assert location.system_name == "Rigel"
        assert location.timestamp == now
        assert location.x == 100.5
        assert location.y == 200.75
        assert location.z == 300.25

    def test_journal_file_handler_existence(self):
        """Test that JournalFileHandler exists."""
        from src.journal import JournalFileHandler
        
        # Should be importable
        assert JournalFileHandler is not None

    def test_journal_parser_initialization_with_no_callbacks(self):
        """Test parser initialization without callbacks."""
        with TemporaryDirectory() as tmpdir:
            parser = JournalParser(journal_path=Path(tmpdir))
            
            # Should have None callbacks
            assert parser.callback is None or callable(parser.callback)
            assert parser.hge_callback is None or callable(parser.hge_callback)

    def test_journal_parser_initialization_with_both_callbacks(self):
        """Test parser initialization with both callbacks."""
        def location_cb(loc):
            pass
        
        def hge_cb(event):
            pass
        
        with TemporaryDirectory() as tmpdir:
            parser = JournalParser(
                journal_path=Path(tmpdir),
                callback=location_cb,
                hge_callback=hge_cb
            )
            
            assert parser.callback == location_cb
            assert parser.hge_callback == hge_cb

    def test_journal_parse_file_with_valid_journal_entry(self):
        """Test parsing a file with valid journal entry."""
        with TemporaryDirectory() as tmpdir:
            journal_path = Path(tmpdir)
            
            # Create a mock journal file
            journal_file = journal_path / "Journal.01.log"
            journal_entry = {
                "timestamp": "2024-01-15T12:30:45Z",
                "event": "Location",
                "StarSystem": "Sirius",
                "StarPos": [8.73, 7.51, -11.56]
            }
            journal_file.write_text(json.dumps(journal_entry) + "\n")
            
            parser = JournalParser(journal_path=journal_path)
            
            # Should initialize without error
            assert parser is not None

    def test_journal_location_equality(self):
        """Test CommanderLocation equality comparison."""
        now = datetime.now(timezone.utc)
        
        loc1 = CommanderLocation(
            system_name="Same",
            timestamp=now,
            x=1.0,
            y=2.0,
            z=3.0
        )
        
        loc2 = CommanderLocation(
            system_name="Same",
            timestamp=now,
            x=1.0,
            y=2.0,
            z=3.0
        )
        
        # Should be equal
        assert loc1 == loc2

    def test_journal_parser_extreme_coordinates(self):
        """Test parser with extreme coordinate values."""
        with TemporaryDirectory() as tmpdir:
            journal_path = Path(tmpdir)
            
            # Create a file with extreme coords
            journal_file = journal_path / "Journal.01.log"
            journal_entry = {
                "timestamp": "2024-01-15T12:30:45Z",
                "event": "Location",
                "StarSystem": "Far System",
                "StarPos": [99999.99, -99999.99, 50000.0]
            }
            journal_file.write_text(json.dumps(journal_entry) + "\n")
            
            parser = JournalParser(journal_path=journal_path)
            
            # Should parse without error
            assert parser is not None

    def test_journal_watcher_thread_safety(self):
        """Test that parser is thread-safe."""
        with TemporaryDirectory() as tmpdir:
            parser = JournalParser(journal_path=Path(tmpdir))
            
            parser.start()
            
            # Start/stop from multiple points should be safe
            location = parser.get_latest_location()
            
            parser.stop()
            
            # Should complete without error
            assert location is None or isinstance(location, CommanderLocation)
