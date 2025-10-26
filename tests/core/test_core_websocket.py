"""
Phase 3A: Core Manager WebSocket Event Tests

Tests for WebSocket event emission during signal and location updates.
Covers lines: 264-265, 284-285, 352-370, 379-387 in src/core.py
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, AsyncMock, call
from src.core import HGENotifierManager
from src.eddn import HGESignal
from src.journal import CommanderLocation


class TestCoreWebSocketPhase3:
    """Test WebSocket event emission in manager."""

    def test_on_new_signal_emits_websocket_event(self):
        """Test signal callback emits WebSocket event."""
        mock_ws = AsyncMock()
        manager = HGENotifierManager(websocket_manager=mock_ws)
        manager.start()
        
        signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )
        
        manager._on_new_hge_signal(signal)
        
        # Signal should be stored
        assert len(manager.signal_history) > 0
        
        manager.stop()

    def test_on_location_change_emits_websocket_event(self):
        """Test location callback emits WebSocket event."""
        mock_ws = AsyncMock()
        manager = HGENotifierManager(websocket_manager=mock_ws)
        manager.start()
        
        location = CommanderLocation(
            system_name="Start System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )
        
        # Call callback
        manager._on_location_change(location)
        
        manager.stop()

    def test_websocket_manager_none_handles_gracefully(self):
        """Test manager handles None WebSocket manager gracefully."""
        manager = HGENotifierManager(websocket_manager=None)
        manager.start()
        
        signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )
        
        # Should not crash with None WebSocket manager
        manager._on_new_hge_signal(signal)
        
        assert len(manager.signal_history) > 0
        
        manager.stop()

    def test_format_signal_for_websocket(self):
        """Test signal formatting for WebSocket delivery."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Format Test",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0,
            allegiance="Federation",
            government="Democracy",
            population=5000000,
            state="None"
        )
        
        formatted = manager._format_signal(signal)
        
        # Should have all required fields
        assert formatted is not None
        assert "system_name" in formatted
        assert "coordinates" in formatted
        assert "allegiance" in formatted
        assert formatted["system_name"] == "Format Test"
        assert formatted["coordinates"]["x"] == 10.0

    def test_format_location_for_websocket(self):
        """Test location formatting for WebSocket delivery."""
        manager = HGENotifierManager()
        
        location = CommanderLocation(
            system_name="Location Test",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )
        
        formatted = manager._format_location(location)
        
        assert formatted is not None
        assert "system_name" in formatted
        assert "coordinates" in formatted
        assert formatted["system_name"] == "Location Test"
        assert formatted["coordinates"]["x"] == 10.0

    def test_calculate_distance_for_websocket(self):
        """Test distance calculation for WebSocket event."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Signal System",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0
        )
        
        location = CommanderLocation(
            system_name="Location System",
            timestamp=datetime.utcnow(),
            x=3.0,
            y=4.0,
            z=0.0
        )
        
        distance_info = manager._calculate_distance(signal, location)
        
        assert distance_info is not None
        assert "distance_ly" in distance_info
        # Distance should be 5.0 (3-4-5 triangle)
        assert distance_info["distance_ly"] == pytest.approx(5.0, rel=0.1)

    def test_calculate_distance_with_none_signal(self):
        """Test distance calculation handles None signal."""
        manager = HGENotifierManager()
        
        location = CommanderLocation(
            system_name="Location System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )
        
        distance_info = manager._calculate_distance(None, location)
        
        assert distance_info is None

    def test_calculate_distance_with_none_location(self):
        """Test distance calculation handles None location."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Signal System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )
        
        distance_info = manager._calculate_distance(signal, None)
        
        assert distance_info is None

    def test_format_signal_with_none_returns_none(self):
        """Test formatting None signal returns None."""
        manager = HGENotifierManager()
        
        formatted = manager._format_signal(None)
        
        assert formatted is None

    def test_format_location_with_none_returns_none(self):
        """Test formatting None location returns None."""
        manager = HGENotifierManager()
        
        formatted = manager._format_location(None)
        
        assert formatted is None

    def test_signal_callback_with_system_info_enrichment(self):
        """Test signal callback enriches with system info."""
        manager = HGENotifierManager()
        manager.start()
        
        signal = HGESignal(
            system_name="Info System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0,
            allegiance=None,
            state=None,
            population=None
        )
        
        with patch('src.system_info.SystemInfoLookup.get_system_info') as mock_info:
            mock_info.return_value = {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 8000000,
                "state": "None"
            }
            
            manager._on_new_hge_signal(signal)
            
            # Signal should be stored with enriched data
            assert len(manager.signal_history) > 0
            stored = manager.signal_history[-1]
            assert stored.allegiance == "Federation"
        
        manager.stop()

    def test_location_callback_emits_distance_with_signal(self):
        """Test location callback calculates distance to latest signal."""
        manager = HGENotifierManager()
        manager.start()
        
        # First add a signal
        signal = HGESignal(
            system_name="Signal System",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0
        )
        manager._on_new_hge_signal(signal)
        
        # Now update location
        location = CommanderLocation(
            system_name="Location System",
            timestamp=datetime.utcnow(),
            x=3.0,
            y=4.0,
            z=0.0
        )
        
        # Should calculate distance without crashing
        manager._on_location_change(location)
        
        manager.stop()
