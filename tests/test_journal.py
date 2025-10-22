"""Tests for journal parsing."""

from datetime import datetime

import pytest

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
