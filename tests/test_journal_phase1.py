"""Additional tests for journal enhancements in Phase 1."""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from src.journal import JournalParser, CommanderLocation


class TestJournalPhase1:
    """Test Phase 1 journal enhancements."""

    def test_journal_parser_with_directory(self):
        """Test journal parser with actual journal files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            journal_dir = Path(tmpdir)
            
            # Create sample journal file
            journal_file = journal_dir / "Journal.220101010101.01.log"
            
            entries = [
                {
                    "timestamp": "2022-01-01T01:01:01Z",
                    "event": "Location",
                    "StarSystem": "Sol",
                    "StarPos": [0.0, 0.0, 0.0],
                },
                {
                    "timestamp": "2022-01-01T02:01:01Z",
                    "event": "FSDJump",
                    "StarSystem": "Sirius",
                    "StarPos": [8.6, 0.0, -2.0],
                },
            ]
            
            with open(journal_file, "w") as f:
                for entry in entries:
                    f.write(json.dumps(entry) + "\n")
            
            parser = JournalParser(journal_path=journal_dir)
            parser.start()

            location = parser.get_latest_location()
            assert location is not None
            # Should have the last location (FSDJump to Sirius)
            assert location.system_name == "Sirius"
            assert location.x == 8.6

            parser.stop()

    def test_journal_parser_callback(self):
        """Test journal parser callback functionality."""
        locations = []

        def callback(location: CommanderLocation):
            locations.append(location)

        with tempfile.TemporaryDirectory() as tmpdir:
            journal_dir = Path(tmpdir)
            
            # Create sample journal file
            journal_file = journal_dir / "Journal.220101010101.01.log"
            
            entries = [
                {
                    "timestamp": "2022-01-01T01:01:01Z",
                    "event": "Location",
                    "StarSystem": "Sol",
                    "StarPos": [0.0, 0.0, 0.0],
                },
            ]
            
            with open(journal_file, "w") as f:
                for entry in entries:
                    f.write(json.dumps(entry) + "\n")

            parser = JournalParser(journal_path=journal_dir, callback=callback)
            parser.start()

            parser._scan_latest_journal()
            parser.stop()

    def test_process_journal_entry(self):
        """Test processing individual journal entries."""
        parser = JournalParser()

        # Test Location event
        location_entry = {
            "event": "Location",
            "timestamp": "2025-10-22T10:30:45Z",
            "StarSystem": "Shinrarta Dezhra",
            "StarPos": [55.72, -49.50, 17.40],
        }

        parser._process_journal_entry(location_entry)
        assert parser.latest_location is not None
        assert parser.latest_location.system_name == "Shinrarta Dezhra"

    def test_parse_timestamp(self):
        """Test timestamp parsing."""
        parser = JournalParser()

        timestamp_str = "2025-10-22T10:30:45Z"
        dt = parser._parse_timestamp(timestamp_str)

        assert dt.year == 2025
        assert dt.month == 10
        assert dt.day == 22

    def test_parse_invalid_timestamp(self):
        """Test parsing invalid timestamps."""
        parser = JournalParser()

        # Should return current time for invalid timestamps
        dt = parser._parse_timestamp("invalid")
        assert isinstance(dt, datetime)
        assert dt.year >= 2025  # Should be recent
