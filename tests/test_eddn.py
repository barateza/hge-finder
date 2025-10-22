"""Tests for EDDN module."""

from datetime import datetime, timedelta

import pytest

from src.eddn import EDDNMonitor, HGESignal


class TestHGESignal:
    """Test HGE Signal dataclass."""

    def test_signal_creation(self) -> None:
        """Test creating an HGE signal."""
        signal = HGESignal(
            system_name="Shinrarta Dezhra",
            timestamp=datetime.utcnow(),
            x=55.7,
            y=-49.5,
            z=17.4,
        )
        assert signal.system_name == "Shinrarta Dezhra"
        assert signal.x == 55.7

    def test_signal_age_human_readable(self) -> None:
        """Test human-readable signal age."""
        # Test seconds ago
        signal = HGESignal(
            system_name="Test",
            timestamp=datetime.utcnow() - timedelta(seconds=30),
        )
        assert "s ago" in signal.age_human_readable()

        # Test minutes ago
        signal = HGESignal(
            system_name="Test",
            timestamp=datetime.utcnow() - timedelta(minutes=5),
        )
        assert "m ago" in signal.age_human_readable()

        # Test hours ago
        signal = HGESignal(
            system_name="Test",
            timestamp=datetime.utcnow() - timedelta(hours=2),
        )
        assert "h ago" in signal.age_human_readable()

        # Test days ago
        signal = HGESignal(
            system_name="Test",
            timestamp=datetime.utcnow() - timedelta(days=3),
        )
        assert "d ago" in signal.age_human_readable()


class TestEDDNMonitor:
    """Test EDDN monitoring functionality."""

    def test_eddn_monitor_mock_mode(self) -> None:
        """Test EDDN monitor in mock mode."""
        monitor = EDDNMonitor(mock_mode=True)
        assert monitor.mock_mode is True
        
        monitor.start()
        signal = monitor.get_latest_signal()
        
        assert signal is not None
        assert signal.system_name == "Shinrarta Dezhra"
        assert signal.x == 55.71905517578125

    def test_eddn_monitor_latest_signal(self) -> None:
        """Test getting latest signal."""
        monitor = EDDNMonitor(mock_mode=True)
        monitor.start()
        
        signal = monitor.get_latest_signal()
        assert signal is not None
        assert isinstance(signal, HGESignal)
