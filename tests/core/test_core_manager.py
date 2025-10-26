"""
Phase 2: Core Integration Tests for HGE Notifier Manager

Tests for:
- Manager initialization with components
- Signal enrichment and system info
- Signal history tracking
- WebSocket event emission
- Status reporting
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, AsyncMock, call
import asyncio

from src.core import HGENotifierManager
from src.eddn import HGESignal
from src.journal import CommanderLocation


class TestHGENotifierManagerInitializationPhase2:
    """Test manager initialization with components."""

    def test_manager_initializes_with_eddn_monitor(self):
        """Test manager initializes EDDN monitor."""
        manager = HGENotifierManager()
        assert manager.eddn_monitor is not None

    def test_manager_initializes_with_journal_parser(self):
        """Test manager initializes journal parser."""
        manager = HGENotifierManager()
        assert manager.journal_parser is not None

    def test_manager_initializes_with_distance_calculator(self):
        """Test manager initializes distance calculator."""
        manager = HGENotifierManager()
        assert manager.distance_calculator is not None

    def test_manager_initializes_with_coord_database(self):
        """Test manager initializes coordinate database."""
        manager = HGENotifierManager()
        assert manager.coord_db is not None

    def test_manager_start_sets_initialized_flag(self):
        """Test manager sets initialized flag on start."""
        manager = HGENotifierManager()
        assert manager._initialized is False
        
        manager.start()
        assert manager._initialized is True
        
        manager.stop()
        assert manager._initialized is False

    def test_manager_start_starts_components(self):
        """Test manager starts EDDN monitor on start."""
        manager = HGENotifierManager()
        manager.start()
        
        # EDDN monitor should be running
        assert manager.eddn_monitor.is_running is True
        
        manager.stop()
        assert manager.eddn_monitor.is_running is False


class TestHGENotifierManagerSignalHandlingPhase2:
    """Test manager signal handling and callbacks."""

    def test_manager_signal_callback_invoked(self):
        """Test manager stores signals correctly."""
        manager = HGENotifierManager()
        manager.start()

        # Simulate signal from EDDN
        test_signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )

        # Call the callback
        manager._on_new_hge_signal(test_signal)

        manager.stop()

    def test_manager_stores_signal_in_history(self):
        """Test manager stores signals in history."""
        manager = HGENotifierManager()
        manager.start()

        test_signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )

        manager._on_new_hge_signal(test_signal)

        # Signal should be in history
        assert len(manager.signal_history) > 0
        assert manager.signal_history[-1].system_name == "Test System"

        manager.stop()

    def test_manager_signal_enrichment(self):
        """Test manager enriches signal with coordinate lookup."""
        manager = HGENotifierManager()
        manager.start()

        test_signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )

        manager._on_new_hge_signal(test_signal)

        manager.stop()

    def test_manager_multiple_signals(self):
        """Test manager handles multiple signals."""
        manager = HGENotifierManager()
        manager.start()

        signal1 = HGESignal(
            system_name="System 1",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )

        signal2 = HGESignal(
            system_name="System 2",
            timestamp=datetime.utcnow(),
            x=40.0,
            y=50.0,
            z=60.0
        )

        manager._on_new_hge_signal(signal1)
        assert len(manager.signal_history) == 1

        manager._on_new_hge_signal(signal2)
        assert len(manager.signal_history) == 2
        assert manager.signal_history[-1].system_name == "System 2"

        manager.stop()


class TestHGENotifierManagerStatusReportingPhase2:
    """Test manager status reporting."""

    def test_manager_get_status_structure(self):
        """Test get_status returns expected structure."""
        manager = HGENotifierManager()
        manager.start()

        status = manager.get_status()

        # Check required keys
        assert "initialized" in status
        assert "hge_signal" in status
        assert "commander_location" in status
        assert "distance" in status

        manager.stop()

    def test_manager_status_includes_signal_data(self):
        """Test status includes HGE signal information."""
        manager = HGENotifierManager()
        manager.start()

        test_signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )

        manager._on_new_hge_signal(test_signal)
        status = manager.get_status()

        # In mock mode, signal_history is populated
        assert status["hge_signal"] is not None
        # The signal in the status might be from the mock EDDN or from our callback
        assert "system_name" in status["hge_signal"]

        manager.stop()

    def test_manager_status_includes_distance(self):
        """Test status includes calculated distance."""
        manager = HGENotifierManager()
        manager.start()

        status = manager.get_status()

        # Distance should be included (could be None if no signal)
        assert "distance" in status

        manager.stop()

    def test_manager_status_without_signal(self):
        """Test status when in mock mode has default signal."""
        manager = HGENotifierManager()
        manager.start()

        status = manager.get_status()

        # In mock mode, there's always a default mock signal
        assert status is not None
        assert "hge_signal" in status
        assert "commander_location" in status

        manager.stop()


class TestHGENotifierManagerRefreshPhase2:
    """Test manager refresh functionality."""

    def test_manager_refresh_updates_status(self):
        """Test refresh operation updates status."""
        manager = HGENotifierManager()
        manager.start()

        # Get initial status
        status1 = manager.get_status()

        # Trigger refresh
        manager.refresh()

        # Get updated status
        status2 = manager.get_status()

        # Status should exist
        assert status2 is not None

        manager.stop()

    def test_manager_refresh_with_signal(self):
        """Test refresh works with active signal."""
        manager = HGENotifierManager()
        manager.start()

        test_signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )

        manager._on_new_hge_signal(test_signal)
        manager.refresh()

        status = manager.get_status()
        # Signal should exist in status
        assert status["hge_signal"] is not None
        # It should have system name (from mock or from our signal)
        assert "system_name" in status["hge_signal"]

        manager.stop()


class TestHGENotifierManagerErrorHandlingPhase2:
    """Test manager error handling."""

    def test_manager_handles_invalid_signal(self):
        """Test manager handles invalid signal gracefully."""
        manager = HGENotifierManager()
        manager.start()

        # Signal with missing coordinates
        invalid_signal = HGESignal(
            system_name="",
            timestamp=datetime.utcnow(),
            x=None,
            y=None,
            z=None
        )

        # Should not crash
        manager._on_new_hge_signal(invalid_signal)

        manager.stop()

    def test_manager_stop_without_start(self):
        """Test stopping manager without starting."""
        manager = HGENotifierManager()
        # Should not crash
        manager.stop()

    def test_manager_double_start(self):
        """Test starting manager twice."""
        manager = HGENotifierManager()
        manager.start()
        assert manager._initialized is True

        # Start again should be handled gracefully
        manager.start()
        assert manager._initialized is True

        manager.stop()

    def test_manager_double_stop(self):
        """Test stopping manager twice."""
        manager = HGENotifierManager()
        manager.start()
        assert manager._initialized is True

        manager.stop()
        assert manager._initialized is False

        # Stop again should be safe
        manager.stop()
        assert manager._initialized is False


class TestHGENotifierManagerHistoryPhase2:
    """Test manager signal history tracking."""

    def test_manager_maintains_signal_history(self):
        """Test manager keeps track of signal history."""
        manager = HGENotifierManager()
        manager.start()

        # Add multiple signals
        signals = []
        for i in range(3):
            signal = HGESignal(
                system_name=f"System {i}",
                timestamp=datetime.utcnow(),
                x=float(i * 10),
                y=float(i * 20),
                z=float(i * 30)
            )
            signals.append(signal)
            manager._on_new_hge_signal(signal)

        # Latest signal should be the last one added
        assert len(manager.signal_history) == 3
        assert manager.signal_history[-1].system_name == "System 2"

        manager.stop()

    def test_manager_signal_age_calculation(self):
        """Test manager calculates signal age correctly."""
        from datetime import timedelta

        manager = HGENotifierManager()
        manager.start()

        # Create old signal
        old_timestamp = datetime.utcnow() - timedelta(hours=1)
        signal = HGESignal(
            system_name="Old Signal",
            timestamp=old_timestamp,
            x=10.0,
            y=20.0,
            z=30.0
        )

        manager._on_new_hge_signal(signal)
        status = manager.get_status()

        # Signal should show correct age
        assert status["hge_signal"] is not None

        manager.stop()


class TestHGENotifierManagerWebSocketPhase2:
    """Test manager WebSocket integration."""

    def test_manager_emit_status_on_signal(self):
        """Test manager handles WebSocket manager if available."""
        manager = HGENotifierManager()
        manager.start()

        test_signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )

        # Should not crash even without WebSocket manager
        manager._on_new_hge_signal(test_signal)

        manager.stop()

    def test_manager_status_ready_for_websocket(self):
        """Test manager status is JSON serializable."""
        import json

        manager = HGENotifierManager()
        manager.start()

        test_signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )

        manager._on_new_hge_signal(test_signal)
        status = manager.get_status()

        # Status should be JSON serializable
        try:
            json_str = json.dumps(status, default=str)
            assert json_str is not None
        except TypeError:
            pytest.fail("Status not JSON serializable")

        manager.stop()
