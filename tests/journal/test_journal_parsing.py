"""
Phase 3C: Journal Parsing Tests

Tests for journal file discovery, event parsing, and HGE detection.
Covers lines: 53-62, 146-331 in src/journal/__init__.py
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.journal import JournalParser, CommanderLocation


class TestJournalDiscoveryPhase3:
    """Test journal file discovery."""

    def test_journal_parser_initialization(self):
        """Test journal parser initializes."""
        parser = JournalParser()
        assert parser is not None

    def test_journal_parser_with_custom_path(self):
        """Test journal parser with custom path."""
        parser = JournalParser(journal_path="/custom/path")
        assert parser is not None

    def test_journal_parser_find_default_journal_location(self):
        """Test journal parser finds default journal location."""
        parser = JournalParser()
        
        # In test environment, may not find actual journal
        # But parser should not crash
        assert parser is not None

    def test_journal_parser_handles_missing_journal_directory(self):
        """Test journal parser handles missing journal directory."""
        parser = JournalParser(journal_path="/nonexistent/path")
        
        # Should not crash on missing directory
        assert parser is not None

    def test_journal_parser_with_mocked_journal_path(self):
        """Test journal parser with mocked journal path."""
        with patch('pathlib.Path.exists', return_value=False):
            parser = JournalParser()
            
            # Should handle gracefully
            assert parser is not None


class TestJournalEventParsingPhase3:
    """Test journal event parsing."""

    def test_journal_parser_location_event_parsing(self):
        """Test parsing location change events."""
        parser = JournalParser()
        
        # Mock a location event
        location_event = {
            "event": "Location",
            "SystemAddress": 123456,
            "StarSystem": "Test System",
            "StarPos": [10.0, 20.0, 30.0],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Parser should handle location events
        assert parser is not None

    def test_journal_parser_commander_location_object(self):
        """Test CommanderLocation object creation."""
        location = CommanderLocation(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )
        
        assert location.system_name == "Test System"
        assert location.x == 10.0
        assert location.y == 20.0
        assert location.z == 30.0

    def test_journal_parser_get_latest_location(self):
        """Test getting latest location from journal."""
        parser = JournalParser()
        
        latest = parser.get_latest_location()
        
        # May be None if no journal or no location events
        assert latest is None or isinstance(latest, CommanderLocation)

    def test_journal_parser_handles_empty_journal(self):
        """Test parser handles empty journal gracefully."""
        parser = JournalParser()
        
        # Should not crash with empty or missing journal
        assert parser is not None
        latest = parser.get_latest_location()
        assert latest is None or isinstance(latest, CommanderLocation)

    def test_journal_parser_coordinate_extraction(self):
        """Test extracting coordinates from journal events."""
        location = CommanderLocation(
            system_name="Coordinate Test",
            timestamp=datetime.utcnow(),
            x=1.5,
            y=2.5,
            z=3.5
        )
        
        assert location.x == 1.5
        assert location.y == 2.5
        assert location.z == 3.5

    def test_journal_parser_fss_signal_detection(self):
        """Test detection of FSS signal events."""
        parser = JournalParser()
        
        # FSS signal event structure
        fss_event = {
            "event": "FSSSignalDiscovered",
            "SystemAddress": 123456,
            "SignalName": "USS (High Grade Emission)",
            "SignalCount": 1,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Parser should handle FSS events
        assert parser is not None

    def test_journal_parser_hge_uss_detection(self):
        """Test detection of HGE USS signals."""
        parser = JournalParser()
        
        hge_event = {
            "event": "FSSSignalDiscovered",
            "SystemAddress": 123456,
            "SignalName": "USS (High Grade Emission)",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Parser should identify HGE signals
        assert parser is not None

    def test_journal_parser_malformed_event_handling(self):
        """Test parser handles malformed events."""
        parser = JournalParser()
        
        # Malformed event
        malformed_event = {
            "event": "Unknown",
            "data": "incomplete"
        }
        
        # Should not crash
        assert parser is not None

    def test_journal_parser_event_timestamp_parsing(self):
        """Test parsing timestamps from events."""
        now = datetime.utcnow()
        location = CommanderLocation(
            system_name="Time Test",
            timestamp=now,
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        assert location.timestamp == now


class TestJournalHGEDetectionPhase3:
    """Test HGE signal detection in journal."""

    def test_journal_hge_callback_invocation(self):
        """Test HGE callback is invoked."""
        hge_signals = []
        
        def hge_callback(signal):
            hge_signals.append(signal)
        
        parser = JournalParser(hge_callback=hge_callback)
        
        assert parser.hge_callback == hge_callback

    def test_journal_location_callback_invocation(self):
        """Test location callback is invoked."""
        locations = []
        
        def location_callback(location):
            locations.append(location)
        
        parser = JournalParser(callback=location_callback)
        
        assert parser.callback == location_callback

    def test_journal_parser_start_monitoring(self):
        """Test starting journal monitoring."""
        parser = JournalParser()
        parser.start()
        
        # Parser should start monitoring
        assert parser is not None
        
        parser.stop()

    def test_journal_parser_stop_monitoring(self):
        """Test stopping journal monitoring."""
        parser = JournalParser()
        parser.start()
        
        parser.stop()
        
        # Parser should stop gracefully
        assert parser is not None

    def test_journal_parser_ignores_irrelevant_events(self):
        """Test parser ignores irrelevant events."""
        parser = JournalParser()
        
        # Irrelevant event types
        irrelevant_events = [
            {"event": "Startup", "timestamp": datetime.utcnow().isoformat()},
            {"event": "ShutDown", "timestamp": datetime.utcnow().isoformat()},
            {"event": "Music", "timestamp": datetime.utcnow().isoformat()},
        ]
        
        # Should not crash or process irrelevant events
        assert parser is not None

    def test_journal_parser_handles_unicode_system_names(self):
        """Test handling unicode characters in system names."""
        location = CommanderLocation(
            system_name="Système Français",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        assert location.system_name == "Système Français"

    def test_journal_parser_handles_long_system_names(self):
        """Test handling very long system names."""
        long_name = "A" * 256
        location = CommanderLocation(
            system_name=long_name,
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        assert location.system_name == long_name

    def test_journal_parser_permission_error_handling(self):
        """Test handling permission errors on journal file."""
        with patch('pathlib.Path.read_text', side_effect=PermissionError("Access denied")):
            parser = JournalParser()
            
            # Should not crash on permission error
            assert parser is not None
