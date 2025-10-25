"""System information lookup module.

Retrieves system properties (allegiance, government, population, state) from EDSM API.
"""

import logging
import requests
from typing import Optional, Dict, Any
from functools import lru_cache
import time

logger = logging.getLogger(__name__)

# EDSM API endpoint
EDSM_API_URL = "https://www.edsm.net/api-v1"

# Cache to avoid repeated API calls for the same system
# Maps system_name -> system_info dict
_system_cache: Dict[str, Any] = {}
_cache_timestamps: Dict[str, float] = {}
CACHE_TTL = 3600  # Cache for 1 hour


class SystemInfoLookup:
    """Lookup system information from EDSM API."""

    @staticmethod
    def get_system_info(system_name: str) -> Optional[Dict[str, Any]]:
        """
        Get system information from EDSM.

        Args:
            system_name: Name of the system

        Returns:
            Dict with keys: allegiance, government, population, state (or None if not found)
        """
        if not system_name:
            return None

        # Check cache first
        cached = SystemInfoLookup._check_cache(system_name)
        if cached is not None:
            return cached

        try:
            # Query EDSM API
            params = {
                "systemName": system_name,
                "showInformation": 1,
                "showFactions": 1,
            }
            
            response = requests.get(
                f"{EDSM_API_URL}/system",
                params=params,
                timeout=5
            )
            
            if response.status_code != 200:
                logger.debug(f"EDSM API returned {response.status_code} for {system_name}")
                # Cache the failure to avoid repeated requests
                _system_cache[system_name] = None
                _cache_timestamps[system_name] = time.time()
                return None
            
            data = response.json()
            
            if not data:
                logger.debug(f"System {system_name} not found in EDSM")
                _system_cache[system_name] = None
                _cache_timestamps[system_name] = time.time()
                return None
            
            # Extract relevant info
            information = data.get("information", {})
            
            system_info = {
                "allegiance": information.get("allegiance"),
                "government": information.get("government"),
                "population": information.get("population"),
                "state": None,
            }
            
            # Extract faction state from information object
            # Note: factionState can be "None" (string) for systems with no active state
            faction_state = information.get("factionState")
            if faction_state and faction_state.lower() != "none":
                system_info["state"] = faction_state
            
            logger.debug(
                f"Found system info for {system_name}: "
                f"allegiance={system_info['allegiance']}, "
                f"state={system_info['state']}"
            )
            
            # Cache the result
            _system_cache[system_name] = system_info
            _cache_timestamps[system_name] = time.time()
            
            return system_info
            
        except requests.exceptions.RequestException as e:
            logger.debug(f"Error querying EDSM for {system_name}: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.debug(f"Error parsing EDSM response for {system_name}: {e}")
            return None

    @staticmethod
    def _check_cache(system_name: str) -> Optional[Dict[str, Any]]:
        """
        Check if system info is in cache and not expired.

        Args:
            system_name: Name of the system

        Returns:
            Cached info or None if not in cache or expired
        """
        if system_name not in _system_cache:
            return None
        
        timestamp = _cache_timestamps.get(system_name, 0)
        if time.time() - timestamp > CACHE_TTL:
            # Cache expired
            del _system_cache[system_name]
            del _cache_timestamps[system_name]
            return None
        
        return _system_cache[system_name]

    @staticmethod
    def clear_cache() -> None:
        """Clear the cache."""
        _system_cache.clear()
        _cache_timestamps.clear()
