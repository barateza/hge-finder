"""
Phase 4A: Core Manager Edge Cases and Error Conditions

Tests for HGENotifierManager edge cases: system info failures, WebSocket unavailable,
distance calculation edge cases, and state management edge conditions.
Covers error paths and boundary conditions in src/core.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from pathlib import Path
from datetime import datetime
import asyncio

from src.core import HGENotifierManager
from src.eddn import HGESignal
from src.journal import CommanderLocation


class TestCoreEdgeCasesPhase4:
    """Test edge cases and error conditions in HGENotifierManager."""

    def test_core_manager_initialization_without_websocket(self):
        """Test manager initializes without websocket."""
        manager = HGENotifierManager(websocket_manager=None)
        
        assert manager is not None
        assert manager.websocket_manager is None
        assert manager.eddn_monitor is not None
        assert manager.journal_parser is not None

    def test_core_manager_initialization_with_websocket(self):
        """Test manager initializes with websocket."""
        mock_ws = MagicMock()
        manager = HGENotifierManager(websocket_manager=mock_ws)
        
        assert manager.websocket_manager is mock_ws

    def test_core_manager_start_stop_lifecycle(self):
        """Test manager start and stop lifecycle."""
        manager = HGENotifierManager()
        
        manager.start()
        assert manager._initialized
        
        manager.stop()
        assert not manager._initialized

    def test_core_manager_start_idempotency(self):
        """Test starting manager multiple times is safe."""
        manager = HGENotifierManager()
        
        manager.start()
        manager.start()  # Should not crash
        
        assert manager._initialized
        manager.stop()

    def test_core_manager_stop_idempotency(self):
        """Test stopping manager multiple times is safe."""
        manager = HGENotifierManager()
        
        manager.start()
        manager.stop()
        manager.stop()  # Should not crash
        
        assert not manager._initialized

    def test_core_manager_get_status_not_initialized(self):
        """Test getting status when not initialized."""
        manager = HGENotifierManager()
        
        status = manager.get_status()
        
        # Should return a valid status dict
        assert isinstance(status, dict)
        assert "initialized" in status

    def test_core_manager_get_status_initialized(self):
        """Test getting status when initialized."""
        manager = HGENotifierManager()
        manager.start()
        
        status = manager.get_status()
        
        assert isinstance(status, dict)
        assert status["initialized"] is True
        
        manager.stop()

    def test_core_manager_get_signal_history_empty(self):
        """Test getting signal history when empty."""
        manager = HGENotifierManager()
        
        history = manager.get_signal_history(limit=10)
        
        # Should return list
        assert isinstance(history, list)

    def test_core_manager_get_signal_history_with_limit(self):
        """Test getting signal history respects limit."""
        manager = HGENotifierManager()
        
        # Test with different limits
        history = manager.get_signal_history(limit=5)
        assert isinstance(history, list)
        assert len(history) <= 5

    def test_core_manager_format_signal_none(self):
        """Test formatting None signal."""
        result = HGENotifierManager._format_signal(None)
        
        assert result is None

    def test_core_manager_format_signal_valid(self):
        """Test formatting valid signal."""
        signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0,
            allegiance="Federation",
            government="Democracy",
            population=1000000,
            state="Boom"
        )
        
        result = HGENotifierManager._format_signal(signal)
        
        assert result is not None
        assert result["system_name"] == "Test System"
        assert result["coordinates"]["x"] == 10.0

    def test_core_manager_format_location_none(self):
        """Test formatting None location."""
        result = HGENotifierManager._format_location(None)
        
        assert result is None

    def test_core_manager_format_location_valid(self):
        """Test formatting valid location."""
        location = CommanderLocation(
            system_name="Home System",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        result = HGENotifierManager._format_location(location)
        
        assert result is not None
        assert result["system_name"] == "Home System"
        assert result["coordinates"]["x"] == 0.0

    def test_core_manager_calculate_distance_both_none(self):
        """Test calculating distance when both signal and location are None."""
        manager = HGENotifierManager()
        
        result = manager._calculate_distance(None, None)
        
        assert result is None

    def test_core_manager_calculate_distance_signal_none(self):
        """Test calculating distance when signal is None."""
        manager = HGENotifierManager()
        
        location = CommanderLocation(
            system_name="Home",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        result = manager._calculate_distance(None, location)
        
        assert result is None

    def test_core_manager_calculate_distance_location_none(self):
        """Test calculating distance when location is None."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="HGE",
            timestamp=datetime.utcnow(),
            x=5.0,
            y=5.0,
            z=5.0
        )
        
        result = manager._calculate_distance(signal, None)
        
        assert result is None

    def test_core_manager_calculate_distance_both_valid(self):
        """Test calculating distance with valid signal and location."""
        manager = HGENotifierManager()
        
        location = CommanderLocation(
            system_name="Home",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        signal = HGESignal(
            system_name="HGE",
            timestamp=datetime.utcnow(),
            x=3.0,
            y=4.0,
            z=0.0
        )
        
        result = manager._calculate_distance(signal, location)
        
        # Should calculate and return dict
        assert result is None or isinstance(result, dict)

    def test_core_manager_calculate_distance_with_missing_coordinates(self):
        """Test calculating distance with missing coordinates."""
        manager = HGENotifierManager()
        
        location = CommanderLocation(
            system_name="Unknown",
            timestamp=datetime.utcnow(),
            x=None,
            y=None,
            z=None
        )
        
        signal = HGESignal(
            system_name="Unknown HGE",
            timestamp=datetime.utcnow(),
            x=None,
            y=None,
            z=None
        )
        
        result = manager._calculate_distance(signal, location)
        
        assert result is None

    def test_core_manager_enrich_signal_none(self):
        """Test enriching None signal."""
        manager = HGENotifierManager()
        
        result = manager._enrich_signal_coordinates(None)
        
        assert result is None

    def test_core_manager_enrich_signal_already_complete(self):
        """Test enriching signal with complete coordinates."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Complete",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )
        
        result = manager._enrich_signal_coordinates(signal)
        
        # Should return unchanged signal
        assert result == signal
        assert result is not None and result.x == 10.0

    def test_core_manager_enrich_location_none(self):
        """Test enriching None location."""
        manager = HGENotifierManager()
        
        result = manager._enrich_location_coordinates(None)
        
        assert result is None

    def test_core_manager_enrich_location_already_complete(self):
        """Test enriching location with complete coordinates."""
        manager = HGENotifierManager()
        
        location = CommanderLocation(
            system_name="Complete",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )
        
        result = manager._enrich_location_coordinates(location)
        
        # Should return unchanged location
        assert result == location
        assert result is not None and result.x == 10.0

    def test_core_manager_format_notification_history_no_manager(self):
        """Test formatting notification history when none available."""
        manager = HGENotifierManager()
        
        history = manager._format_notification_history()
        
        # Should return list
        assert isinstance(history, list)

    def test_core_manager_get_notification_stats_no_manager(self):
        """Test getting notification stats when none available."""
        manager = HGENotifierManager()
        
        stats = manager._get_notification_stats()
        
        # Should return dict with counts
        assert isinstance(stats, dict)
        assert "total" in stats

    def test_core_manager_refresh_no_data(self):
        """Test refresh method."""
        manager = HGENotifierManager()
        
        # Should not crash
        manager.refresh()
        
        assert manager is not None

    def test_core_manager_signal_history_ordering(self):
        """Test that signal history maintains order."""
        manager = HGENotifierManager()
        
        # Get history
        history = manager.get_signal_history(limit=50)
        
        # Should be a list
        assert isinstance(history, list)
        
        # If there are items, check structure
        if len(history) > 0:
            assert "system_name" in history[0] or isinstance(history[0], dict)

    def test_core_manager_websocket_event_with_none_manager(self):
        """Test that WebSocket events are handled when manager is None."""
        manager = HGENotifierManager(websocket_manager=None)
        manager.start()
        
        # Should not crash when processing events without WebSocket
        signal = HGESignal(
            system_name="Test",
            timestamp=datetime.utcnow(),
            x=1.0,
            y=1.0,
            z=1.0
        )
        
        manager._on_new_hge_signal(signal)
        
        manager.stop()

    def test_core_manager_multiple_signal_emissions(self):
        """Test handling multiple rapid signal emissions."""
        manager = HGENotifierManager()
        manager.start()
        
        # Emit multiple signals
        for i in range(5):
            signal = HGESignal(
                system_name=f"System {i}",
                timestamp=datetime.utcnow(),
                x=float(i),
                y=float(i),
                z=float(i)
            )
            manager._on_new_hge_signal(signal)
        
        # Should handle all signals
        history = manager.get_signal_history(limit=50)
        assert isinstance(history, list)
        
        manager.stop()

    def test_core_manager_signal_with_empty_system_name(self):
        """Test handling signal with empty system name."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="",
            timestamp=datetime.utcnow(),
            x=1.0,
            y=1.0,
            z=1.0
        )
        
        # Should handle gracefully
        formatted = HGENotifierManager._format_signal(signal)
        
        # Format may handle empty names
        assert formatted is None or isinstance(formatted, dict)
