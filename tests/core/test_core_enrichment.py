"""
Phase 3A: Core Manager Signal Enrichment Tests

Tests for signal and location enrichment with EDSM system data.
Covers lines: 87-93, 141-163 in src/core.py
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from src.core import HGENotifierManager
from src.eddn import HGESignal
from src.journal import CommanderLocation


class TestCoreEnrichmentPhase3:
    """Test signal enrichment with EDSM system information."""

    def test_enrich_signal_coordinates_success(self):
        """Test enriching signal with coordinates from database."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=None,
            y=None,
            z=None
        )
        
        # Mock coordinate database lookup
        with patch.object(manager.coord_db, 'get_coordinates',
                         return_value=(1.0, 2.0, 3.0)):
            
            enriched_signal = manager._enrich_signal_coordinates(signal)
            
            # Signal should have enriched coordinates
            assert enriched_signal is not None
            assert enriched_signal.x == 1.0
            assert enriched_signal.y == 2.0
            assert enriched_signal.z == 3.0

    def test_enrich_signal_coordinates_missing_db_data(self):
        """Test enrichment handles missing database data gracefully."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Unknown System",
            timestamp=datetime.utcnow(),
            x=None,
            y=None,
            z=None
        )
        
        # Mock database returning None
        with patch.object(manager.coord_db, 'get_coordinates', 
                         return_value=None):
            
            enriched_signal = manager._enrich_signal_coordinates(signal)
            
            # Should return signal with None coordinates
            assert enriched_signal is not None
            assert enriched_signal.system_name == "Unknown System"
            assert enriched_signal.x is None

    def test_enrich_signal_already_has_coordinates(self):
        """Test enrichment skips lookup if coordinates already present."""
        manager = HGENotifierManager()
        
        signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0
        )
        
        # Mock coordinate database lookup (should not be called)
        with patch.object(manager.coord_db, 'get_coordinates',
                         return_value=(1.0, 2.0, 3.0)) as mock_lookup:
            
            enriched = manager._enrich_signal_coordinates(signal)
            
            # Should not have called database
            mock_lookup.assert_not_called()
            # Coordinates should remain unchanged
            assert enriched.x == 10.0
            assert enriched.y == 20.0

    def test_enrich_location_coordinates_success(self):
        """Test enriching location with database coordinates."""
        manager = HGENotifierManager()
        
        location = CommanderLocation(
            system_name="Start System",
            timestamp=datetime.utcnow(),
            x=None,
            y=None,
            z=None
        )
        
        # Mock database lookup
        with patch.object(manager.coord_db, 'get_coordinates',
                         return_value=(10.0, 20.0, 30.0)):
            
            enriched_location = manager._enrich_location_coordinates(location)
            
            assert enriched_location is not None
            assert enriched_location.x == 10.0
            assert enriched_location.y == 20.0
            assert enriched_location.z == 30.0

    def test_enrich_location_coordinates_db_error(self):
        """Test enrichment handles database errors gracefully."""
        manager = HGENotifierManager()
        
        location = CommanderLocation(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=None,
            y=None,
            z=None
        )
        
        # Mock database raising exception
        with patch.object(manager.coord_db, 'get_coordinates',
                         side_effect=Exception("DB error")):
            
            enriched = manager._enrich_location_coordinates(location)
            
            # Should handle error gracefully, return location as-is
            assert enriched is not None
            assert enriched.system_name == "Test System"

    def test_enrich_location_none_handling(self):
        """Test enrichment handles None location gracefully."""
        manager = HGENotifierManager()
        
        enriched = manager._enrich_location_coordinates(None)
        
        assert enriched is None

    def test_enrich_signal_none_handling(self):
        """Test enrichment handles None signal gracefully."""
        manager = HGENotifierManager()
        
        enriched = manager._enrich_signal_coordinates(None)
        
        assert enriched is None

    def test_signal_enrichment_with_system_info_lookup(self):
        """Test signal enrichment with system info lookup in callback."""
        manager = HGENotifierManager()
        manager.start()
        
        test_signal = HGESignal(
            system_name="Test System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=20.0,
            z=30.0,
            allegiance=None,
            state=None,
            population=None
        )
        
        # Mock system info lookup
        with patch('src.system_info.SystemInfoLookup.get_system_info') as mock_info:
            mock_info.return_value = {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 5000000,
                "state": "None"
            }
            
            # Call callback
            manager._on_new_hge_signal(test_signal)
            
            # Signal should be enriched with system info
            assert len(manager.signal_history) > 0
            stored_signal = manager.signal_history[-1]
            assert stored_signal.system_name == "Test System"
        
        manager.stop()

    def test_signal_enrichment_maintains_history(self):
        """Test multiple signals maintain correct history."""
        manager = HGENotifierManager()
        manager.start()
        
        for i in range(3):
            signal = HGESignal(
                system_name=f"System {i}",
                timestamp=datetime.utcnow(),
                x=float(i),
                y=float(i),
                z=float(i)
            )
            manager._on_new_hge_signal(signal)
        
        # All signals should be in history
        assert len(manager.signal_history) == 3
        assert manager.signal_history[0].system_name == "System 0"
        assert manager.signal_history[1].system_name == "System 1"
        assert manager.signal_history[2].system_name == "System 2"
        
        manager.stop()

    def test_enrich_location_partial_coordinates(self):
        """Test enriching location with partial missing coordinates."""
        manager = HGENotifierManager()
        
        location = CommanderLocation(
            system_name="Partial System",
            timestamp=datetime.utcnow(),
            x=10.0,
            y=None,  # Missing
            z=None   # Missing
        )
        
        # Should attempt to enrich
        with patch.object(manager.coord_db, 'get_coordinates',
                         return_value=(10.0, 20.0, 30.0)):
            
            enriched = manager._enrich_location_coordinates(location)
            
            # Should update missing coordinates
            assert enriched.x == 10.0
            assert enriched.y == 20.0
            assert enriched.z == 30.0
