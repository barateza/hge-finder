"""Tests for core manager."""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import pytest

from src.core import HGENotifierManager
from src.eddn import HGESignal
from src.journal import CommanderLocation


class TestHGENotifierManager:
    """Test HGE Notifier Manager."""

    def test_manager_initialization(self) -> None:
        """Test manager can be initialized."""
        manager = HGENotifierManager()
        assert manager is not None
        assert manager._initialized is False

    def test_manager_start_stop(self) -> None:
        """Test manager start and stop."""
        manager = HGENotifierManager()
        manager.start()
        assert manager._initialized is True
        
        manager.stop()
        assert manager._initialized is False

    def test_manager_get_status(self) -> None:
        """Test getting manager status."""
        manager = HGENotifierManager()
        manager.start()
        
        status = manager.get_status()
        assert status is not None
        # Phase 3: Status now returns aggregated systems instead of single signal
        assert "active_systems" in status
        assert "commander_location" in status
        assert "total_unique_systems" in status
        assert "total_reports" in status
        assert "nearest_distance_ly" in status
        assert "initialized" in status
        
        manager.stop()

    def test_manager_status_contains_data(self) -> None:
        """Test that status contains expected data."""
        manager = HGENotifierManager()
        manager.start()
        
        status = manager.get_status()
        
        # Phase 3: Should have aggregated systems (list) instead of single signal
        assert isinstance(status["active_systems"], list)
        assert status["commander_location"] is not None
        
        # Should have system aggregation statistics
        assert isinstance(status["total_unique_systems"], int)
        assert isinstance(status["total_reports"], int)
        
        manager.stop()


class TestCoreOrchestrationEdgeCases:
    """Test Core manager orchestration edge cases (Phase 3.3.B)."""

    def test_manager_with_missing_location_data(self) -> None:
        """Test manager status when location is unavailable."""
        manager = HGENotifierManager()
        manager.start()
        
        # Mock journal parser to return None
        with patch.object(manager.journal_parser, 'get_latest_location', return_value=None):
            status = manager.get_status()
            
            # Should handle gracefully
            assert status is not None
            assert status["commander_location"] is None
        
        manager.stop()

    def test_manager_with_missing_signal_data(self) -> None:
        """Test manager status when no signals have been received yet."""
        manager = HGENotifierManager()
        manager.start()
        
        status = manager.get_status()
        
        # Phase 3: Should handle gracefully with empty systems list
        assert status is not None
        assert isinstance(status["active_systems"], list)
        # Before any signals, active_systems should be empty
        assert status["total_unique_systems"] == 0
        
        manager.stop()

    def test_manager_distance_calculation_with_complete_data(self) -> None:
        """Test distance calculation with complete coordinate data."""
        manager = HGENotifierManager()
        manager.start()
        
        status = manager.get_status()
        
        # Phase 3: Distance should be calculated for active systems if available
        # If active_systems list has entries and location has coordinates
        if status["active_systems"] and status["commander_location"]:
            # nearest_distance_ly should be a float or None
            assert status["nearest_distance_ly"] is None or isinstance(status["nearest_distance_ly"], (int, float))
        
        manager.stop()

    def test_manager_distance_calculation_with_missing_coordinates(self) -> None:
        """Test distance calculation when coordinates are missing."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=None,
            y=None,
            z=None,
        )
        
        location = CommanderLocation(
            system_name="Test Location",
            timestamp=datetime.utcnow(),
            x=None,
            y=None,
            z=None,
        )
        
        with patch.object(manager.eddn_monitor, 'get_latest_signal', return_value=signal):
            with patch.object(manager.journal_parser, 'get_latest_location', return_value=location):
                # Phase 3: Process the signal through merger
                manager._on_new_hge_signal(signal)
                status = manager.get_status()
                
                # Should handle gracefully - nearest_distance_ly may be None (no coords)
                assert status["nearest_distance_ly"] is None or isinstance(status["nearest_distance_ly"], (int, float))
                # Should still have active_systems list (even if no distances calculated)
                assert isinstance(status["active_systems"], list)

    def test_manager_callback_on_new_signal_with_location(self) -> None:
        """Test callback execution when new signal and location available."""
        manager = HGENotifierManager()
        manager.start()
        
        signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=55.0,
            y=-49.0,
            z=17.0,
        )
        
        location = CommanderLocation(
            system_name="Sol",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0,
        )
        
        with patch.object(manager.journal_parser, 'get_latest_location', return_value=location):
            # Call the callback - notification system is disabled (None) but should handle gracefully
            manager._on_new_hge_signal(signal)
            
            # Verify signal was added to history
            assert len(manager.signal_history) > 0
            assert manager.signal_history[-1].system_name == "Test System"
        
        manager.stop()

    def test_manager_callback_on_new_signal_without_location(self) -> None:
        """Test callback execution when signal available but location missing."""
        manager = HGENotifierManager()
        manager.start()
        
        signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=55.0,
            y=-49.0,
            z=17.0,
        )
        
        with patch.object(manager.journal_parser, 'get_latest_location', return_value=None):
            # Should not raise exception
            manager._on_new_hge_signal(signal)
        
        manager.stop()

    def test_manager_location_callback(self) -> None:
        """Test callback when location changes."""
        manager = HGENotifierManager()
        manager.start()
        
        location = CommanderLocation(
            system_name="Sol",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0,
        )
        
        # Call the callback - should not raise exception
        manager._on_location_change(location)
        
        manager.stop()

    def test_manager_error_in_signal_callback(self) -> None:
        """Test signal callback handles errors gracefully."""
        manager = HGENotifierManager()
        manager.start()
        
        signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
        )
        
        # Mock journal parser to raise error to test exception handling
        with patch.object(manager.journal_parser, 'get_latest_location', side_effect=Exception("Test error")):
            # Should not raise exception - callback handles errors gracefully
            manager._on_new_hge_signal(signal)
            
            # Verify signal was still added to history
            assert len(manager.signal_history) > 0
            assert manager.signal_history[-1].system_name == "Test System"
        
        manager.stop()

    def test_manager_enrich_signal_with_db_lookup(self) -> None:
        """Test enriching signal coordinates from database."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Sol",
            timestamp=datetime.utcnow(),
            x=None,
            y=None,
            z=None,
        )
        
        # Mock database to return coordinates
        with patch.object(manager.coord_db, 'get_coordinates', return_value=(0.0, 0.0, 0.0)):
            enriched = manager._enrich_signal_coordinates(signal)
            
            # Should have enriched coordinates
            assert enriched is not None

    def test_manager_enrich_signal_already_has_coordinates(self) -> None:
        """Test enriching signal when coordinates already present."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Sol",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0,
        )
        
        with patch.object(manager.coord_db, 'get_coordinates') as mock_get:
            enriched = manager._enrich_signal_coordinates(signal)
            
            # Should not call database for lookup
            assert not mock_get.called
            assert enriched is signal

    def test_manager_enrich_signal_db_error(self) -> None:
        """Test signal enrichment handles database errors."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Unknown System",
            timestamp=datetime.utcnow(),
            x=None,
            y=None,
            z=None,
        )
        
        # Make database raise error
        with patch.object(manager.coord_db, 'get_coordinates', side_effect=Exception("DB error")):
            enriched = manager._enrich_signal_coordinates(signal)
            
            # Should return original signal
            assert enriched is signal

    def test_manager_enrich_location_with_db_lookup(self) -> None:
        """Test enriching location coordinates from database."""
        manager = HGENotifierManager()
        
        location = CommanderLocation(
            system_name="Sol",
            timestamp=datetime.utcnow(),
            x=None,
            y=None,
            z=None,
        )
        
        # Mock database to return coordinates
        with patch.object(manager.coord_db, 'get_coordinates', return_value=(0.0, 0.0, 0.0)):
            enriched = manager._enrich_location_coordinates(location)
            
            # Should have enriched coordinates
            assert enriched is not None

    def test_manager_refresh(self) -> None:
        """Test refresh operation."""
        manager = HGENotifierManager()
        manager.start()
        
        # Should not raise exception
        manager.refresh()
        
        manager.stop()

    def test_manager_format_signal_none(self) -> None:
        """Test formatting None signal."""
        formatted = HGENotifierManager._format_signal(None)
        assert formatted is None

    def test_manager_format_signal_with_data(self) -> None:
        """Test formatting signal with complete data."""
        signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=55.0,
            y=-49.0,
            z=17.0,
        )
        
        formatted = HGENotifierManager._format_signal(signal)
        
        assert formatted is not None
        assert formatted["system_name"] == "Test System"
        assert formatted["coordinates"]["x"] == 55.0

    def test_manager_format_location_none(self) -> None:
        """Test formatting None location."""
        formatted = HGENotifierManager._format_location(None)
        assert formatted is None

    def test_manager_format_location_with_data(self) -> None:
        """Test formatting location with complete data."""
        location = CommanderLocation(
            system_name="Sol",
            timestamp=datetime.utcnow(),
            x=0.0,
            y=0.0,
            z=0.0,
        )
        
        formatted = HGENotifierManager._format_location(location)
        
        assert formatted is not None
        assert formatted["system_name"] == "Sol"
        assert formatted["coordinates"]["x"] == 0.0

    def test_manager_format_notification_history(self) -> None:
        """Test formatting notification history."""
        manager = HGENotifierManager()
        manager.start()
        
        # Verify manager has expected structure
        assert hasattr(manager, 'notification_manager')
        
        manager.stop()

    def test_manager_double_start(self) -> None:
        """Test starting manager twice."""
        manager = HGENotifierManager()
        manager.start()
        
        # Start again - should handle gracefully
        manager.start()
        
        manager.stop()

    def test_manager_stop_without_start(self) -> None:
        """Test stopping manager without starting."""
        manager = HGENotifierManager()
        
        # Should not raise exception
        manager.stop()

    def test_manager_status_after_stop(self) -> None:
        """Test getting status after stopping manager."""
        manager = HGENotifierManager()
        manager.start()
        manager.stop()
        
        status = manager.get_status()
        
        # Should still return status
        assert status is not None
        assert status["initialized"] is False

    def test_manager_multiple_start_stop_cycles(self) -> None:
        """Test multiple start/stop cycles."""
        manager = HGENotifierManager()
        
        for _ in range(3):
            manager.start()
            assert manager._initialized is True
            
            manager.stop()
            assert manager._initialized is False


# ============================================================================
# CORE MANAGER ERROR HANDLING AND EDGE CASES
# ============================================================================


class TestCoreManagerErrorHandling:
    """Test Core manager error handling and edge cases."""

    def test_manager_no_signal(self) -> None:
        """Test manager handles missing HGE signal."""
        manager = HGENotifierManager()
        manager.start()
        
        # Mock EDDN monitor to return no signal
        with patch.object(manager.eddn_monitor, 'get_latest_signal', return_value=None):
            # Get status should not crash
            status = manager.get_status()
            
            assert status is not None
        
        manager.stop()

    def test_manager_no_location(self) -> None:
        """Test manager handles missing commander location."""
        manager = HGENotifierManager()
        manager.start()
        
        # Mock journal parser to return no location
        with patch.object(manager.journal_parser, 'get_latest_location', return_value=None):
            # Get status should not crash
            status = manager.get_status()
            
            assert status is not None
        
        manager.stop()

