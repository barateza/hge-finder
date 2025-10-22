"""Additional tests for EDDN enhancements in Phase 1."""

import pytest
import json
from datetime import datetime

from src.eddn import EDDNMonitor, HGESignal


class TestEDDNEnhanced:
    """Test Phase 1 EDDN enhancements."""

    def test_eddn_monitor_with_callback(self):
        """Test EDDN monitor with callback function."""
        callback_signals = []

        def callback(signal: HGESignal):
            callback_signals.append(signal)

        monitor = EDDNMonitor(mock_mode=True, callback=callback)
        monitor.start()

        # Mock data should trigger callback
        assert monitor.latest_signal is not None

        monitor.stop()

    def test_hge_message_detection(self):
        """Test detection of HGE messages."""
        monitor = EDDNMonitor(mock_mode=True)

        # Test USS schema
        uss_message = {
            "$schemaRef": "https://eddn.edcd.io/schemas/journal/1/uss",
            "StarSystem": "Test System",
            "timestamp": "2025-10-22T10:30:45Z",
            "StarPos": [10.0, 20.0, 30.0],
        }
        assert monitor._is_hge_message(uss_message)

        # Test codex schema
        codex_message = {
            "$schemaRef": "https://eddn.edcd.io/schemas/journal/1/codex",
            "StarSystem": "Test System",
        }
        assert monitor._is_hge_message(codex_message)

        # Test non-HGE message
        other_message = {
            "$schemaRef": "https://eddn.edcd.io/schemas/journal/1/other",
        }
        assert not monitor._is_hge_message(other_message)

    def test_hge_signal_parsing(self):
        """Test parsing HGE signal from EDDN message."""
        monitor = EDDNMonitor(mock_mode=True)

        message = {
            "StarSystem": "Shinrarta Dezhra",
            "timestamp": "2025-10-22T10:30:45Z",
            "StarPos": [55.72, -49.50, 17.40],
        }

        signal = monitor._parse_hge_signal(message)

        assert signal is not None
        assert signal.system_name == "Shinrarta Dezhra"
        assert signal.x == 55.72
        assert signal.y == -49.50
        assert signal.z == 17.40

    def test_hge_signal_parsing_missing_data(self):
        """Test parsing HGE signal with missing data."""
        monitor = EDDNMonitor(mock_mode=True)

        # Missing system name
        message = {
            "timestamp": "2025-10-22T10:30:45Z",
            "StarPos": [10.0, 20.0, 30.0],
        }

        signal = monitor._parse_hge_signal(message)
        assert signal is None

        # Missing coordinates
        message = {
            "StarSystem": "Test System",
            "timestamp": "2025-10-22T10:30:45Z",
        }

        signal = monitor._parse_hge_signal(message)
        assert signal is not None  # Should still parse, coords are optional
        assert signal.x is None
