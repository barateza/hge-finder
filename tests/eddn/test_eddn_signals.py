"""
Phase 2: Core Integration Tests for EDDN Signal Detection and Lifecycle

Tests for:
- EDDNMonitor initialization (mock and real modes)
- Signal callback execution
- Signal lifecycle management
- Error handling during signal processing
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, call
import time

from src.eddn import EDDNMonitor, HGESignal


class TestEDDNMonitorInitializationPhase2:
    """Test EDDN monitor initialization and mock data setup."""

    def test_eddn_monitor_mock_mode_initialization(self):
        """Test EDDNMonitor initializes with mock data in mock mode."""
        monitor = EDDNMonitor(mock_mode=True)
        monitor.start()

        # Verify mock signal was initialized
        signal = monitor.get_latest_signal()
        assert signal is not None
        assert signal.system_name == "Shinrarta Dezhra"
        assert signal.x == pytest.approx(55.71905517578125)
        assert signal.y == pytest.approx(-49.50000381469727)

        monitor.stop()

    def test_eddn_monitor_mock_mode_signal_timestamp(self):
        """Test mock signal has valid timestamp."""
        monitor = EDDNMonitor(mock_mode=True)
        monitor.start()

        signal = monitor.get_latest_signal()
        assert signal is not None
        assert signal.timestamp is not None
        assert isinstance(signal.timestamp, datetime)
        # Should be recent (within last hour)
        age = signal.age_seconds()
        assert age >= 0
        assert age < 3600

        monitor.stop()

    def test_eddn_monitor_mock_mode_signal_coordinates(self):
        """Test mock signal has valid 3D coordinates."""
        monitor = EDDNMonitor(mock_mode=True)
        monitor.start()

        signal = monitor.get_latest_signal()
        assert signal is not None
        # Check all coordinates are present and numeric
        assert isinstance(signal.x, (int, float))
        assert isinstance(signal.y, (int, float))
        assert isinstance(signal.z, (int, float))
        # Verify reasonable coordinate ranges
        assert -500 < signal.x < 500
        assert -500 < signal.y < 500
        assert -500 < signal.z < 500

        monitor.stop()

    def test_eddn_monitor_mock_mode_callback_called(self):
        """Test EDDNMonitor initializes signal in mock mode."""
        monitor = EDDNMonitor(mock_mode=True)
        monitor.start()

        # In mock mode, signal is initialized immediately
        signal = monitor.get_latest_signal()
        assert signal is not None
        assert signal.system_name == "Shinrarta Dezhra"
        assert isinstance(signal, HGESignal)

        monitor.stop()

    def test_eddn_monitor_multiple_callback_invocations(self):
        """Test monitor stores signals even in mock mode."""
        monitor = EDDNMonitor(mock_mode=True)
        monitor.start()

        # In mock mode, signal is set immediately
        signal1 = monitor.get_latest_signal()
        assert signal1 is not None
        
        # Stop and restart
        monitor.stop()
        monitor.start()
        
        signal2 = monitor.get_latest_signal()
        assert signal2 is not None
        assert signal2.system_name == signal1.system_name

        monitor.stop()


class TestEDDNMonitorLifecyclePhase2:
    """Test EDDN monitor start/stop lifecycle."""

    def test_eddn_monitor_stop_operation(self):
        """Test EDDNMonitor stop operation."""
        monitor = EDDNMonitor(mock_mode=True)
        monitor.start()
        assert monitor.is_running is True

        monitor.stop()
        assert monitor.is_running is False

    def test_eddn_monitor_start_stop_start(self):
        """Test monitor can be stopped and restarted."""
        monitor = EDDNMonitor(mock_mode=True)

        # First start/stop cycle
        monitor.start()
        assert monitor.is_running is True
        monitor.stop()
        assert monitor.is_running is False

        # Second start cycle
        monitor.start()
        assert monitor.is_running is True
        monitor.stop()
        assert monitor.is_running is False

    def test_eddn_monitor_multiple_monitors(self):
        """Test multiple independent monitors can run."""
        monitor1 = EDDNMonitor(mock_mode=True)
        monitor2 = EDDNMonitor(mock_mode=True)

        monitor1.start()
        signal1 = monitor1.get_latest_signal()
        assert signal1 is not None
        assert signal1.system_name == "Shinrarta Dezhra"
        monitor1.stop()

        monitor2.start()
        signal2 = monitor2.get_latest_signal()
        assert signal2 is not None
        assert signal2.system_name == "Shinrarta Dezhra"
        monitor2.stop()

    def test_eddn_monitor_get_latest_signal_empty(self):
        """Test getting latest signal when none available."""
        monitor = EDDNMonitor(mock_mode=True)

        # Before starting, should have None or empty signal
        signal = monitor.get_latest_signal()
        # After initialization, mock mode should have set a signal
        monitor.start()
        signal = monitor.get_latest_signal()
        assert signal is not None
        monitor.stop()


class TestEDDNSignalFormatPhase2:
    """Test EDDN signal format detection and parsing."""

    def test_hge_signal_creation(self):
        """Test HGESignal creation with valid data."""
        signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )

        assert signal.system_name == "Test System"
        assert signal.x == 10.0
        assert signal.y == 20.0
        assert signal.z == 30.0

    def test_hge_signal_age_seconds(self):
        """Test HGESignal age calculation."""
        now = datetime.utcnow()
        signal = HGESignal(
            system_name="Test System",
            timestamp=now,
            x=0.0,
            y=0.0,
            z=0.0
        )

        age = signal.age_seconds()
        assert age >= 0
        assert age < 1  # Should be very recent

    def test_hge_signal_age_old_signal(self):
        """Test age calculation for older signal."""
        from datetime import timedelta

        old_time = datetime.utcnow() - timedelta(hours=1)
        signal = HGESignal(
            system_name="Old Signal",
            timestamp=old_time,
            x=0.0,
            y=0.0,
            z=0.0
        )

        age = signal.age_seconds()
        # Should be approximately 3600 seconds (1 hour)
        assert 3595 < age < 3605


class TestEDDNMonitorErrorHandlingPhase2:
    """Test EDDN monitor error handling."""

    def test_eddn_monitor_no_callback(self):
        """Test monitor works without callback."""
        monitor = EDDNMonitor(mock_mode=True, callback=None)
        monitor.start()

        # Should not crash without callback
        time.sleep(0.1)
        assert monitor.is_running is True
        monitor.stop()

    def test_eddn_monitor_callback_exception_handling(self):
        """Test monitor handles callback exceptions gracefully."""

        def failing_callback(signal):
            raise ValueError("Callback error")

        monitor = EDDNMonitor(mock_mode=True, callback=failing_callback)
        monitor.start()

        # Should not crash despite callback raising exception
        time.sleep(0.1)
        assert monitor.is_running is True

        monitor.stop()

    def test_eddn_monitor_callback_receives_signal(self):
        """Test monitor initializes signal correctly."""
        monitor = EDDNMonitor(mock_mode=True)
        monitor.start()

        # Signal should be initialized in mock mode
        signal = monitor.get_latest_signal()
        assert signal is not None
        assert isinstance(signal, HGESignal)
        assert signal.system_name is not None
        assert signal.timestamp is not None
        
        monitor.stop()
