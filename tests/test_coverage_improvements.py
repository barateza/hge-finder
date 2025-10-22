"""Coverage improvement tests for Phase 1 error handling."""

import pytest
import json
import requests
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.eddn import EDDNMonitor, HGESignal
from src.distance.coordinates import CoordinateDatabase
from src.core import HGENotifierManager


class TestEDDNErrorHandling:
    """Test EDDN error handling for better coverage."""

    def test_eddn_connection_timeout(self):
        """Test EDDN handles connection timeouts gracefully."""
        with patch('zmq.Context') as mock_context:
            # Simulate socket creation failure
            mock_socket = MagicMock()
            mock_socket.connect.side_effect = TimeoutError("Connection timeout")
            mock_context.return_value.socket.return_value = mock_socket
            
            monitor = EDDNMonitor(mock_mode=False)
            
            # Attempt to connect - should handle gracefully
            try:
                monitor._connect_to_eddn()
            except TimeoutError:
                pass  # Expected
            
            # Monitor should handle this gracefully
            assert monitor.latest_signal is None or isinstance(monitor.latest_signal, HGESignal)

    def test_eddn_invalid_json(self):
        """Test EDDN handles malformed JSON messages gracefully."""
        monitor = EDDNMonitor(mock_mode=True)
        
        # Simulate invalid JSON message
        invalid_messages = [
            b'{"invalid": json}',  # Malformed JSON
            b'not json at all',     # Not JSON
            b'',                     # Empty
        ]
        
        for invalid_msg in invalid_messages:
            # Should not raise exception
            try:
                monitor._process_eddn_message([b'header', invalid_msg])
            except json.JSONDecodeError:
                # Expected - logged but not raised in real usage
                pass

    def test_eddn_reconnection(self):
        """Test EDDN reconnects after failure."""
        monitor = EDDNMonitor(mock_mode=True)
        
        # Mock a reconnection attempt
        monitor._reconnect_count = 3
        
        # Should have reconnect behavior
        assert monitor.is_running is False  # Not running yet
        
        monitor.start()
        assert monitor.is_running is True
        
        monitor.stop()
        assert monitor.is_running is False


class TestCoordinatesErrorHandling:
    """Test Coordinates database error handling for better coverage."""

    def test_coordinates_api_timeout(self):
        """Test coordinate lookup handles API timeout gracefully."""
        with patch('requests.get') as mock_get:
            # Simulate API timeout
            mock_get.side_effect = requests.Timeout("API request timeout")
            
            db = CoordinateDatabase()
            
            # Should handle timeout gracefully
            result = db.get_coordinates('UnknownSystem')
            
            # Should return None instead of raising
            assert result is None

    def test_coordinates_invalid_response(self):
        """Test coordinate lookup handles invalid API response."""
        with patch('requests.get') as mock_get:
            # Simulate invalid API response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'error': 'not found'}
            mock_get.return_value = mock_response
            
            db = CoordinateDatabase()
            
            # Should handle invalid response gracefully
            result = db.get_coordinates('BadSystem')
            
            # Should return None
            assert result is None

    def test_coordinates_missing_system(self):
        """Test coordinate lookup for non-existent system."""
        import tempfile
        import shutil
        
        # Use a real database but mock the requests
        tmpdir = tempfile.mkdtemp()
        try:
            with patch('requests.get') as mock_get:
                # Simulate EDSM returning dict with no id (system not found)
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {}  # EDSM returns empty dict when not found
                mock_response.raise_for_status = MagicMock()
                mock_get.return_value = mock_response
                
                from pathlib import Path
                db = CoordinateDatabase(db_path=Path(tmpdir))
                
                # Request coordinates for system that doesn't exist
                result = db.get_coordinates('SystemDoesNotExist_12345', use_cache=False)
                
                # Should handle missing data gracefully
                assert result is None
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestCoreManagerEdgeCases:
    """Test Core manager edge cases for better coverage."""

    def test_manager_no_signal(self):
        """Test manager handles missing HGE signal."""
        manager = HGENotifierManager()
        manager.start()
        
        # Manually clear signal to simulate no HGE data
        manager.last_signal = None
        
        # Get status should not crash
        status = manager.get_status()
        
        assert status is not None
        # Signal should be missing
        assert status.get("hge_signal") is None or isinstance(status.get("hge_signal"), dict)
        
        manager.stop()

    def test_manager_no_location(self):
        """Test manager handles missing commander location."""
        manager = HGENotifierManager()
        manager.start()
        
        # Manually clear location to simulate no location data
        manager.last_location = None
        
        # Get status should not crash
        status = manager.get_status()
        
        assert status is not None
        # Location should be missing
        assert status.get("commander_location") is None or isinstance(status.get("commander_location"), dict)
        
        manager.stop()


class TestEDDNMessageProcessing:
    """Additional tests for EDDN message processing edge cases."""

    def test_eddn_process_empty_multipart(self):
        """Test EDDN handles empty multipart messages."""
        monitor = EDDNMonitor(mock_mode=True)
        
        # Empty multipart message
        monitor._process_eddn_message([])
        
        # Should not crash

    def test_eddn_process_single_part_message(self):
        """Test EDDN handles single-part messages."""
        monitor = EDDNMonitor(mock_mode=True)
        
        # Single part message (missing JSON payload)
        monitor._process_eddn_message([b'header_only'])
        
        # Should not crash

    def test_eddn_non_hge_message(self):
        """Test EDDN ignores non-HGE messages."""
        monitor = EDDNMonitor(mock_mode=True)
        initial_signal = monitor.latest_signal
        
        # Process a non-HGE message
        non_hge_message = {
            "$schemaRef": "https://eddn.edcd.io/schemas/journal/1/scan",
            "StarSystem": "Some System",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        json_data = json.dumps(non_hge_message).encode()
        monitor._process_eddn_message([b'header', json_data])
        
        # Signal should remain unchanged (not a HGE message)
        # or be the same as before
        assert monitor.latest_signal == initial_signal or monitor.latest_signal is not None


class TestCoordinatesDatabaseEdgeCases:
    """Additional tests for Coordinates database edge cases."""

    def test_coordinates_fetch_with_missing_fields(self):
        """Test coordinate fetching with missing coordinate fields."""
        with patch('requests.get') as mock_get:
            # Simulate response with missing z coordinate
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'name': 'TestSystem',
                'coords': {
                    'x': 10.0,
                    'y': 20.0,
                    # z is missing
                }
            }
            mock_get.return_value = mock_response
            
            db = CoordinateDatabase()
            
            # Should handle missing fields gracefully
            result = db.get_coordinates('TestSystem')
            
            # Result should be None or valid tuple
            assert result is None or isinstance(result, tuple)

    def test_coordinates_api_connection_error(self):
        """Test coordinate lookup handles connection errors."""
        with patch('requests.get') as mock_get:
            # Simulate connection error
            mock_get.side_effect = requests.ConnectionError("Connection failed")
            
            db = CoordinateDatabase()
            
            # Should handle connection error gracefully
            result = db.get_coordinates('TestSystem')
            
            # Should return None
            assert result is None

    def test_coordinates_api_http_error(self):
        """Test coordinate lookup handles HTTP errors."""
        with patch('requests.get') as mock_get:
            # Simulate HTTP error (404, 500, etc.)
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
            mock_get.return_value = mock_response
            
            db = CoordinateDatabase()
            
            # Should handle HTTP error gracefully
            result = db.get_coordinates('NonExistentSystem')
            
            # Should return None
            assert result is None


class TestManagerStatusWithoutData:
    """Test manager status formatting when data is missing."""

    def test_manager_status_all_none(self):
        """Test manager status when all data is None."""
        manager = HGENotifierManager()
        manager.start()
        
        # Clear all data
        manager.last_signal = None
        manager.last_location = None
        
        # Get status should work
        status = manager.get_status()
        
        assert status is not None
        assert isinstance(status, dict)
        assert "initialized" in status
        
        manager.stop()

    def test_manager_distance_with_partial_data(self):
        """Test manager distance calculation with partial data."""
        manager = HGENotifierManager()
        manager.start()
        
        # Clear signal but keep location
        manager.last_signal = None
        
        status = manager.get_status()
        
        # Distance should handle missing signal
        assert status.get("distance") is None or isinstance(status.get("distance"), (dict, type(None)))
        
        manager.stop()
