"""Tests for system_info module - EDSM API integration."""

import pytest
import time
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout, ConnectionError, RequestException
from src.system_info import SystemInfoLookup, _system_cache, _cache_timestamps


class TestSystemInfoLookupBasic:
    """Test basic system information lookup functionality."""

    def setup_method(self):
        """Clear cache before each test."""
        _system_cache.clear()
        _cache_timestamps.clear()

    def test_get_system_info_with_empty_system_name(self):
        """Test that empty system name returns None."""
        result = SystemInfoLookup.get_system_info("")
        assert result is None

    @patch('src.system_info.requests.get')
    def test_get_system_info_successful_lookup(self, mock_get):
        """Test successful system information retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
                "factionState": "Boom",
            }
        }
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is not None
        assert result["allegiance"] == "Federation"
        assert result["government"] == "Democracy"
        assert result["population"] == 1000000
        assert result["state"] == "Boom"
        mock_get.assert_called_once()

    @patch('src.system_info.requests.get')
    def test_get_system_info_api_error_404(self, mock_get):
        """Test API returning 404 error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("NonexistentSystem")
        
        assert result is None
        # Should cache the failure
        assert "NonexistentSystem" in _system_cache

    @patch('src.system_info.requests.get')
    def test_get_system_info_api_error_500(self, mock_get):
        """Test API returning 500 error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is None

    @patch('src.system_info.requests.get')
    def test_get_system_info_empty_response(self, mock_get):
        """Test empty JSON response from API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is None

    @patch('src.system_info.requests.get')
    def test_get_system_info_missing_information_field(self, mock_get):
        """Test response without 'information' field."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123}
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is not None
        assert result["allegiance"] is None
        assert result["government"] is None
        assert result["population"] is None
        assert result["state"] is None


class TestSystemInfoCaching:
    """Test caching behavior."""

    def setup_method(self):
        """Clear cache before each test."""
        _system_cache.clear()
        _cache_timestamps.clear()

    @patch('src.system_info.requests.get')
    def test_cache_hit_returns_cached_data(self, mock_get):
        """Test that cached data is returned without API call."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
            }
        }
        mock_get.return_value = mock_response

        # First call - should hit API
        result1 = SystemInfoLookup.get_system_info("Sol")
        assert mock_get.call_count == 1
        
        # Second call - should return cached data
        result2 = SystemInfoLookup.get_system_info("Sol")
        assert mock_get.call_count == 1  # No additional API call
        assert result1 == result2

    @patch('src.system_info.requests.get')
    def test_cache_miss_calls_api(self, mock_get):
        """Test that uncached system triggers API call."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Empire",
                "government": "Autocracy",
                "population": 2000000,
            }
        }
        mock_get.return_value = mock_response

        SystemInfoLookup.get_system_info("Achenar")
        mock_get.assert_called_once()

    @patch('src.system_info.requests.get')
    def test_cache_expiration(self, mock_get):
        """Test that cache expires after TTL."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
            }
        }
        mock_get.return_value = mock_response

        # First call
        SystemInfoLookup.get_system_info("Sol")
        assert mock_get.call_count == 1
        
        # Manually expire cache
        _cache_timestamps["Sol"] = time.time() - 3700  # More than CACHE_TTL (3600)
        
        # Second call - should hit API again since cache expired
        SystemInfoLookup.get_system_info("Sol")
        assert mock_get.call_count == 2

    @patch('src.system_info.requests.get')
    def test_cache_failure(self, mock_get):
        """Test that failed lookups result in cache entry (cached None)."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Call for nonexistent system
        result1 = SystemInfoLookup.get_system_info("NonexistentSystem")
        assert result1 is None
        
        # System should be in cache even though lookup failed
        assert "NonexistentSystem" in _system_cache
        assert _system_cache["NonexistentSystem"] is None


class TestSystemInfoNetworkErrors:
    """Test network error handling."""

    def setup_method(self):
        """Clear cache before each test."""
        _system_cache.clear()
        _cache_timestamps.clear()

    @patch('src.system_info.requests.get')
    def test_connection_timeout(self, mock_get):
        """Test handling of connection timeout."""
        mock_get.side_effect = Timeout("Connection timed out")

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is None

    @patch('src.system_info.requests.get')
    def test_connection_error(self, mock_get):
        """Test handling of connection error."""
        mock_get.side_effect = ConnectionError("Connection failed")

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is None

    @patch('src.system_info.requests.get')
    def test_request_exception(self, mock_get):
        """Test handling of generic request exception."""
        mock_get.side_effect = RequestException("Generic error")

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is None


class TestSystemInfoResponseParsing:
    """Test response parsing and field extraction."""

    def setup_method(self):
        """Clear cache before each test."""
        _system_cache.clear()
        _cache_timestamps.clear()

    @patch('src.system_info.requests.get')
    def test_parse_faction_state_boom(self, mock_get):
        """Test parsing of faction state 'Boom'."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
                "factionState": "Boom",
            }
        }
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is not None
        assert result["state"] == "Boom"

    @patch('src.system_info.requests.get')
    def test_parse_faction_state_none_string(self, mock_get):
        """Test parsing of faction state 'None' (string)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
                "factionState": "None",
            }
        }
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is not None
        assert result["state"] is None

    @patch('src.system_info.requests.get')
    def test_parse_faction_state_none_uppercase(self, mock_get):
        """Test parsing of faction state 'NONE' (uppercase)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
                "factionState": "NONE",
            }
        }
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is not None
        assert result["state"] is None

    @patch('src.system_info.requests.get')
    def test_parse_missing_faction_state(self, mock_get):
        """Test parsing when faction state is missing."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
            }
        }
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is not None
        assert result["state"] is None

    @patch('src.system_info.requests.get')
    def test_parse_all_fields_present(self, mock_get):
        """Test parsing with all fields present."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Empire",
                "government": "Autocracy",
                "population": 5000000,
                "factionState": "Boom",
            }
        }
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Achenar")
        
        assert result is not None
        assert result["allegiance"] == "Empire"
        assert result["government"] == "Autocracy"
        assert result["population"] == 5000000
        assert result["state"] == "Boom"

    @patch('src.system_info.requests.get')
    def test_parse_all_fields_missing(self, mock_get):
        """Test parsing when all information fields are missing."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {}
        }
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is not None
        assert result["allegiance"] is None
        assert result["government"] is None
        assert result["population"] is None
        assert result["state"] is None


class TestSystemInfoMalformedResponses:
    """Test handling of malformed API responses."""

    def setup_method(self):
        """Clear cache before each test."""
        _system_cache.clear()
        _cache_timestamps.clear()

    @patch('src.system_info.requests.get')
    def test_invalid_json_response(self, mock_get):
        """Test handling of invalid JSON response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is None

    @patch('src.system_info.requests.get')
    def test_response_with_extra_fields(self, mock_get):
        """Test that extra fields in response don't cause errors."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 123,
            "name": "Sol",
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
            },
            "extra_field": "should be ignored"
        }
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is not None
        assert result["allegiance"] == "Federation"


class TestSystemInfoCacheManagement:
    """Test cache management methods."""

    def setup_method(self):
        """Clear cache before each test."""
        _system_cache.clear()
        _cache_timestamps.clear()

    @patch('src.system_info.requests.get')
    def test_clear_cache(self, mock_get):
        """Test that clear_cache empties the cache."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
            }
        }
        mock_get.return_value = mock_response

        # Add some data to cache
        SystemInfoLookup.get_system_info("Sol")
        assert len(_system_cache) > 0
        
        # Clear cache
        SystemInfoLookup.clear_cache()
        
        assert len(_system_cache) == 0
        assert len(_cache_timestamps) == 0

    @patch('src.system_info.requests.get')
    def test_cache_cleared_after_clear_method(self, mock_get):
        """Test that subsequent calls hit API after clear."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
            }
        }
        mock_get.return_value = mock_response

        # First call
        SystemInfoLookup.get_system_info("Sol")
        assert mock_get.call_count == 1
        
        # Clear and call again
        SystemInfoLookup.clear_cache()
        SystemInfoLookup.get_system_info("Sol")
        
        assert mock_get.call_count == 2


class TestSystemInfoCheckCache:
    """Test the _check_cache method."""

    def setup_method(self):
        """Clear cache before each test."""
        _system_cache.clear()
        _cache_timestamps.clear()

    def test_check_cache_empty(self):
        """Test _check_cache with empty cache."""
        result = SystemInfoLookup._check_cache("NonexistentSystem")
        assert result is None

    @patch('src.system_info.requests.get')
    def test_check_cache_hit(self, mock_get):
        """Test _check_cache returns cached data."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
            }
        }
        mock_get.return_value = mock_response

        # Populate cache
        SystemInfoLookup.get_system_info("Sol")
        
        # Check cache
        result = SystemInfoLookup._check_cache("Sol")
        
        assert result is not None
        assert result["allegiance"] == "Federation"

    def test_check_cache_expired(self):
        """Test _check_cache removes expired data."""
        # Manually add expired data to cache
        _system_cache["Sol"] = {"allegiance": "Federation"}
        _cache_timestamps["Sol"] = time.time() - 3700  # More than CACHE_TTL
        
        result = SystemInfoLookup._check_cache("Sol")
        
        assert result is None
        assert "Sol" not in _system_cache
        assert "Sol" not in _cache_timestamps

    def test_check_cache_very_old_timestamp(self):
        """Test _check_cache with very old timestamp treats cache as expired."""
        # Add data with old timestamp
        _system_cache["Sol"] = {"allegiance": "Federation"}
        _cache_timestamps["Sol"] = time.time() - 86400  # 1 day ago
        
        result = SystemInfoLookup._check_cache("Sol")
        
        # Should expire since timestamp is very old
        assert result is None


class TestSystemInfoEdgeCases:
    """Test edge cases and special scenarios."""

    def setup_method(self):
        """Clear cache before each test."""
        _system_cache.clear()
        _cache_timestamps.clear()

    @patch('src.system_info.requests.get')
    def test_system_name_with_special_characters(self, mock_get):
        """Test system names with special characters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
            }
        }
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Beagle Point A-0")
        
        assert result is not None
        mock_get.assert_called_once()

    @patch('src.system_info.requests.get')
    def test_system_name_with_unicode(self, mock_get):
        """Test system names with unicode characters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
            }
        }
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Système Klingon")
        
        assert result is not None

    @patch('src.system_info.requests.get')
    def test_very_large_population(self, mock_get):
        """Test parsing of very large population values."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 999999999999999,
            }
        }
        mock_get.return_value = mock_response

        result = SystemInfoLookup.get_system_info("Sol")
        
        assert result is not None
        assert result["population"] == 999999999999999

    @patch('src.system_info.requests.get')
    def test_various_allegiances(self, mock_get):
        """Test parsing of various allegiance types."""
        allegiances = ["Federation", "Empire", "Alliance", "Independent"]
        
        for allegiance in allegiances:
            _system_cache.clear()
            _cache_timestamps.clear()
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "information": {
                    "allegiance": allegiance,
                    "government": "Democracy",
                    "population": 1000000,
                }
            }
            mock_get.return_value = mock_response

            result = SystemInfoLookup.get_system_info("TestSystem")
            
            assert result is not None
            assert result["allegiance"] == allegiance

    @patch('src.system_info.requests.get')
    def test_various_governments(self, mock_get):
        """Test parsing of various government types."""
        governments = ["Democracy", "Dictatorship", "Autocracy", "Corporate"]
        
        for government in governments:
            _system_cache.clear()
            _cache_timestamps.clear()
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "information": {
                    "allegiance": "Federation",
                    "government": government,
                    "population": 1000000,
                }
            }
            mock_get.return_value = mock_response

            result = SystemInfoLookup.get_system_info("TestSystem")
            
            assert result is not None
            assert result["government"] == government


class TestSystemInfoAPICallParameters:
    """Test that API calls are made with correct parameters."""

    def setup_method(self):
        """Clear cache before each test."""
        _system_cache.clear()
        _cache_timestamps.clear()

    @patch('src.system_info.requests.get')
    def test_api_called_with_correct_url(self, mock_get):
        """Test that API is called with correct EDSM URL."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
            }
        }
        mock_get.return_value = mock_response

        SystemInfoLookup.get_system_info("Sol")
        
        # Check that requests.get was called with EDSM URL
        call_args = mock_get.call_args
        assert call_args is not None
        assert "https://www.edsm.net/api-v1/system" in call_args[0][0]

    @patch('src.system_info.requests.get')
    def test_api_called_with_system_name_param(self, mock_get):
        """Test that API call includes system name parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
            }
        }
        mock_get.return_value = mock_response

        SystemInfoLookup.get_system_info("Sol")
        
        # Check that params include systemName
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["params"]["systemName"] == "Sol"
        assert call_kwargs["params"]["showInformation"] == 1
        assert call_kwargs["params"]["showFactions"] == 1

    @patch('src.system_info.requests.get')
    def test_api_timeout_parameter(self, mock_get):
        """Test that API call uses timeout parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "information": {
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
            }
        }
        mock_get.return_value = mock_response

        SystemInfoLookup.get_system_info("Sol")
        
        # Check that timeout is set to 5 seconds
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["timeout"] == 5
