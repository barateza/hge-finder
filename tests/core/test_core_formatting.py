"""
Phase 3A: Core Manager Formatting and Distance Tests

Tests for formatting signals/locations and distance calculations.
Covers lines: 352-370, 398-452 in src/core.py
"""

import pytest
from datetime import datetime
from src.core import HGENotifierManager
from src.eddn import HGESignal
from src.journal import CommanderLocation


class TestCoreFormattingPhase3:
    """Test signal and location formatting."""

    def test_format_signal_complete(self):
        """Test complete signal formatting."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Complete System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0,
            allegiance="Alliance",
            government="Cooperative",
            population=2000000,
            state="War"
        )
        
        formatted = manager._format_signal(signal)
        
        assert formatted["system_name"] == "Complete System"
        assert formatted["coordinates"]["x"] == 10.0
        assert formatted["coordinates"]["y"] == 20.0
        assert formatted["coordinates"]["z"] == 30.0
        assert formatted["allegiance"] == "Alliance"
        assert formatted["government"] == "Cooperative"
        assert "materials" in formatted

    def test_format_signal_with_missing_fields(self):
        """Test signal formatting with missing optional fields."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Minimal System",
            timestamp=datetime.utcnow(),
            x=1.0,
            y=2.0,
            z=3.0
        )
        
        formatted = manager._format_signal(signal)
        
        assert formatted is not None
        assert formatted["system_name"] == "Minimal System"
        assert formatted["allegiance"] is None

    def test_format_location_complete(self):
        """Test complete location formatting."""
        manager = HGENotifierManager()
        
        location = CommanderLocation(
            system_name="Complete Location",
            timestamp=datetime.utcnow(),
            x=100.0,
            y=200.0,
            z=300.0
        )
        
        formatted = manager._format_location(location)
        
        assert formatted["system_name"] == "Complete Location"
        assert formatted["coordinates"]["x"] == 100.0
        assert formatted["coordinates"]["y"] == 200.0
        assert formatted["coordinates"]["z"] == 300.0

    def test_calculate_distance_simple(self):
        """Test distance calculation with simple coordinates."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Signal",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        location = CommanderLocation(
            system_name="Location",
            timestamp=datetime.utcnow(),
            x=3.0,
            y=4.0,
            z=0.0
        )
        
        distance_info = manager._calculate_distance(signal, location)
        
        assert distance_info is not None
        assert "distance_ly" in distance_info
        assert distance_info["distance_ly"] == pytest.approx(5.0, rel=0.1)

    def test_calculate_distance_3d(self):
        """Test distance calculation in 3D space."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Signal",
            timestamp=datetime.utcnow(),
            x=1.0,
            y=2.0,
            z=3.0
        )
        
        location = CommanderLocation(
            system_name="Location",
            timestamp=datetime.utcnow(),
            x=4.0,
            y=6.0,
            z=8.0
        )
        
        distance_info = manager._calculate_distance(signal, location)
        
        assert distance_info is not None
        # sqrt((4-1)^2 + (6-2)^2 + (8-3)^2) = sqrt(9+16+25) = sqrt(50) ≈ 7.07
        assert distance_info["distance_ly"] == pytest.approx(7.07, rel=0.1)

    def test_distance_calculation_same_location(self):
        """Test distance when signal and location are in same system."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Same System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )
        
        location = CommanderLocation(
            system_name="Same System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )
        
        distance_info = manager._calculate_distance(signal, location)
        
        assert distance_info is not None
        assert distance_info["distance_ly"] == pytest.approx(0.0, abs=0.01)

    def test_format_signal_timestamp_iso_format(self):
        """Test signal timestamp is formatted as ISO."""
        manager = HGENotifierManager()
        
        now = datetime.utcnow()
        signal = HGESignal(
            system_name="Time System",
            timestamp=now,
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        formatted = manager._format_signal(signal)
        
        # Should be ISO formatted
        assert isinstance(formatted["timestamp"], str)
        assert "T" in formatted["timestamp"]

    def test_format_location_timestamp_iso_format(self):
        """Test location timestamp is formatted as ISO."""
        manager = HGENotifierManager()
        
        now = datetime.utcnow()
        location = CommanderLocation(
            system_name="Time Location",
            timestamp=now,
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        formatted = manager._format_location(location)
        
        assert isinstance(formatted["timestamp"], str)
        assert "T" in formatted["timestamp"]

    def test_distance_calculation_with_missing_coordinates(self):
        """Test distance calculation when coordinates are incomplete."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Signal",
            timestamp=datetime.utcnow(),
            x=None,
            y=None,
            z=None
        )
        
        location = CommanderLocation(
            system_name="Location",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )
        
        distance_info = manager._calculate_distance(signal, location)
        
        # Should handle missing coordinates gracefully
        # Result depends on how DistanceCalculator handles None
        # But it should not crash
        assert distance_info is None or "distance_ly" in distance_info

    def test_get_status_with_no_signals(self):
        """Test get_status when no signals received yet."""
        manager = HGENotifierManager()
        manager.start()
        
        status = manager.get_status()
        
        assert status is not None
        assert "hge_signal" in status
        assert "commander_location" in status
        assert "distance" in status
        
        manager.stop()

    def test_get_status_with_signal_and_location(self):
        """Test get_status with both signal and location."""
        manager = HGENotifierManager()
        manager.start()
        
        signal = HGESignal(
            system_name="Signal",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        location = CommanderLocation(
            system_name="Location",
            timestamp=datetime.utcnow(),
            x=3.0,
            y=4.0,
            z=0.0
        )
        
        manager._on_new_hge_signal(signal)
        manager._on_location_change(location)
        
        status = manager.get_status()
        
        assert status is not None
        assert status["hge_signal"] is not None
        assert status["commander_location"] is not None
        
        manager.stop()
