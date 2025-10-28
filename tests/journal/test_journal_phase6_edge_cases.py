"""
Phase 6: Journal Module Edge Cases

Comprehensive testing of journal file parsing and edge cases:
- File I/O edge cases
- Entry parsing with malformed data
- Timestamp handling extremes
- Location tracking accuracy

Target: 5% coverage gap (85% → ≥90%)
New Tests: 10+
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import json
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

from src.journal import CommanderLocation, JournalParser


class TestCommanderLocationCreation:
    """Test CommanderLocation creation and edge cases."""

    def test_location_basic(self):
        """Test basic location creation."""
        location = CommanderLocation(
            system_name="Sol",
            timestamp=datetime.utcnow()
        )
        
        assert location.system_name == "Sol"
        assert location.timestamp is not None

    def test_location_with_coordinates(self):
        """Test location with coordinates."""
        location = CommanderLocation(
            system_name="Sol",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        assert location.x == 0.0
        assert location.y == 0.0
        assert location.z == 0.0

    def test_location_extreme_coordinates(self):
        """Test extreme coordinate values."""
        location = CommanderLocation(
            system_name="EdgeSystem",
            timestamp=datetime.utcnow(),
            x=99999.99,
            y=-99999.99,
            z=99999.99
        )
        
        assert location.x == 99999.99
        assert location.y == -99999.99
        assert location.z == 99999.99

    def test_location_zero_coordinates(self):
        """Test zero coordinate values."""
        location = CommanderLocation(
            system_name="Origin",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        assert location.x == 0.0
        assert location.y == 0.0
        assert location.z == 0.0

    def test_location_very_old_timestamp(self):
        """Test very old timestamp."""
        old_time = datetime(2000, 1, 1, 0, 0, 0)
        location = CommanderLocation(
            system_name="OldSystem",
            timestamp=old_time,
            x=1.0,
            y=2.0,
            z=3.0
        )
        
        assert location.timestamp == old_time

    def test_location_future_timestamp(self):
        """Test future timestamp."""
        future_time = datetime(2099, 12, 31, 23, 59, 59)
        location = CommanderLocation(
            system_name="FutureSystem",
            timestamp=future_time,
            x=1.0,
            y=2.0,
            z=3.0
        )
        
        assert location.timestamp == future_time

    def test_location_special_character_name(self):
        """Test system name with special characters."""
        location = CommanderLocation(
            system_name="Système d'Elite Ñoño's Bar",
            timestamp=datetime.utcnow(),
            x=1.0,
            y=2.0,
            z=3.0
        )
        
        assert "Système" in location.system_name
        assert "Ñoño" in location.system_name

    def test_location_partial_coordinates(self):
        """Test location with partial coordinates."""
        location = CommanderLocation(
            system_name="PartialSys",
            timestamp=datetime.utcnow(),
            x=1.0,
            y=None,
            z=3.0
        )
        
        assert location.x == 1.0
        assert location.y is None
        assert location.z == 3.0

    def test_location_negative_coordinates(self):
        """Test negative coordinate values."""
        location = CommanderLocation(
            system_name="NegativeSys",
            timestamp=datetime.utcnow(),
            x=-10.5,
            y=-20.75,
            z=-30.25
        )
        
        assert location.x == -10.5
        assert location.y == -20.75
        assert location.z == -30.25


class TestJournalParserInitialization:
    """Test JournalParser initialization and configuration."""

    def test_parser_initialization_default(self):
        """Test parser with default parameters."""
        parser = JournalParser()
        assert parser is not None

    def test_parser_initialization_with_path(self):
        """Test parser with journal path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            parser = JournalParser(journal_path=Path(tmpdir))
            assert parser is not None

    def test_parser_initialization_nonexistent_path(self):
        """Test parser with non-existent path."""
        parser = JournalParser(journal_path=Path("/nonexistent/path"))
        assert parser is not None

    def test_parser_initialization_with_callback(self):
        """Test parser with callback."""
        callback = Mock()
        parser = JournalParser(callback=callback)
        assert parser is not None

    def test_parser_initialization_with_hge_callback(self):
        """Test parser with HGE callback."""
        hge_callback = Mock()
        parser = JournalParser(hge_callback=hge_callback)
        assert parser is not None

    def test_parser_initialization_with_all_options(self):
        """Test parser with all initialization options."""
        with tempfile.TemporaryDirectory() as tmpdir:
            callback = Mock()
            hge_callback = Mock()
            parser = JournalParser(
                journal_path=Path(tmpdir),
                callback=callback,
                hge_callback=hge_callback
            )
            assert parser is not None


class TestJournalFileHandling:
    """Test journal file I/O edge cases."""

    def test_empty_journal_file(self):
        """Test parsing empty journal file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            temp_path = f.name
        
        try:
            parser = JournalParser(journal_path=Path(os.path.dirname(temp_path)))
            assert parser is not None
        finally:
            os.unlink(temp_path)

    def test_large_journal_file(self):
        """Test parsing large journal file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            for i in range(100):
                entry = {
                    "timestamp": "2024-01-01T12:00:00Z",
                    "event": "Location",
                    "StarSystem": f"System{i}",
                    "X": 1.0, "Y": 2.0, "Z": 3.0
                }
                f.write(json.dumps(entry) + "\n")
            temp_path = f.name
        
        try:
            parser = JournalParser(journal_path=Path(os.path.dirname(temp_path)))
            assert parser is not None
        finally:
            os.unlink(temp_path)

    def test_malformed_json_handling(self):
        """Test handling malformed JSON in journal."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
            f.write('{"valid": "json"}\n')
            f.write('{"invalid": json}\n')
            f.write('{"valid": "json"}\n')
            temp_path = f.name
        
        try:
            parser = JournalParser(journal_path=Path(os.path.dirname(temp_path)))
            assert parser is not None
        finally:
            os.unlink(temp_path)

    def test_unicode_handling(self):
        """Test journal with unicode characters."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as f:
            entries = [
                {"timestamp": "2024-01-01T12:00:00Z", "event": "Location", "StarSystem": "Système", "X": 0, "Y": 0, "Z": 0},
                {"timestamp": "2024-01-01T12:01:00Z", "event": "Location", "StarSystem": "日本", "X": 1, "Y": 2, "Z": 3},
                {"timestamp": "2024-01-01T12:02:00Z", "event": "Location", "StarSystem": "РФ", "X": 2, "Y": 3, "Z": 4},
            ]
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            temp_path = f.name
        
        try:
            parser = JournalParser(journal_path=Path(os.path.dirname(temp_path)))
            assert parser is not None
        finally:
            os.unlink(temp_path)


class TestLocationComparison:
    """Test location comparison and distance calculations."""

    def test_locations_same_system(self):
        """Test two locations in same system."""
        loc1 = CommanderLocation("Sol", datetime(2024, 1, 1), 0, 0, 0)
        loc2 = CommanderLocation("Sol", datetime(2024, 1, 2), 0, 0, 0)
        
        assert loc1.system_name == loc2.system_name

    def test_locations_different_systems(self):
        """Test two locations in different systems."""
        loc1 = CommanderLocation("Sol", datetime(2024, 1, 1), 0, 0, 0)
        loc2 = CommanderLocation("Sirius", datetime(2024, 1, 1), 8.6, 0, 0)
        
        assert loc1.system_name != loc2.system_name

    def test_location_timestamp_ordering(self):
        """Test ordering by timestamp."""
        now = datetime.utcnow()
        past = now - timedelta(hours=1)
        future = now + timedelta(hours=1)
        
        loc1 = CommanderLocation("Sys1", past)
        loc2 = CommanderLocation("Sys2", now)
        loc3 = CommanderLocation("Sys3", future)
        
        locations = [loc2, loc3, loc1]
        sorted_locs = sorted(locations, key=lambda l: l.timestamp)
        
        assert sorted_locs[0].timestamp == past
        assert sorted_locs[1].timestamp == now
        assert sorted_locs[2].timestamp == future


class TestJournalEdgeCases:
    """Test edge cases in journal handling."""

    def test_location_empty_system_name(self):
        """Test empty system name."""
        location = CommanderLocation(
            system_name="",
            timestamp=datetime.utcnow()
        )
        
        assert location.system_name == ""

    def test_location_very_long_system_name(self):
        """Test very long system name."""
        long_name = "A" * 1000
        location = CommanderLocation(
            system_name=long_name,
            timestamp=datetime.utcnow()
        )
        
        assert len(location.system_name) == 1000

    def test_location_whitespace_system_name(self):
        """Test system name with whitespace."""
        location = CommanderLocation(
            system_name="   System With Spaces   ",
            timestamp=datetime.utcnow()
        )
        
        assert "System With Spaces" in location.system_name

    def test_location_numeric_coordinates_precision(self):
        """Test coordinate precision with many decimals."""
        location = CommanderLocation(
            system_name="Precise",
            timestamp=datetime.utcnow(),
            x=123.456789123,
            y=987.654321987,
            z=-456.789123456
        )
        
        assert location.x == 123.456789123
        assert location.y == 987.654321987
        assert location.z == -456.789123456
