"""Coordinate database module - System coordinate management."""

import json
import logging
import sqlite3
import threading
import time
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime, timedelta

import requests


logger = logging.getLogger(__name__)


class CoordinateDatabase:
    """Manage system coordinates with caching."""

    EDSM_API_URL = "https://www.edsm.net/api-v1/system"
    DB_NAME = "coordinates.db"
    CACHE_EXPIRY_DAYS = 30

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """
        Initialize coordinate database.

        Args:
            db_path: Path to store the SQLite database.
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data"
        
        self.db_path = db_path
        self.db_file = db_path / self.DB_NAME
        self._lock = threading.RLock()
        self._init_database()

    def _init_database(self) -> None:
        """Initialize the SQLite database."""
        try:
            self.db_path.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Create systems table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS systems (
                        id INTEGER PRIMARY KEY,
                        system_name TEXT UNIQUE NOT NULL,
                        x REAL,
                        y REAL,
                        z REAL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        source TEXT DEFAULT 'edsm'
                    )
                """)
                
                # Create index for faster lookups
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_system_name 
                    ON systems(system_name)
                """)
                
                conn.commit()
                logger.info(f"Database initialized at {self.db_file}")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def get_coordinates(
        self,
        system_name: str,
        use_cache: bool = True,
    ) -> Optional[Tuple[float, float, float]]:
        """
        Get coordinates for a system.

        Args:
            system_name: Name of the system
            use_cache: If True, use cached data if available

        Returns:
            Tuple of (x, y, z) coordinates or None if not found
        """
        with self._lock:
            # Check cache first
            if use_cache:
                coords = self._get_from_cache(system_name)
                if coords:
                    return coords

            # Try EDSM API with retry
            coords = self._fetch_from_edsm_with_retry(system_name, retries=2)
            
            if coords:
                self._store_in_cache(system_name, coords)
                return coords

            return None

    def _fetch_from_edsm_with_retry(
        self,
        system_name: str,
        retries: int = 2,
    ) -> Optional[Tuple[float, float, float]]:
        """
        Fetch coordinates from EDSM API with retry logic.

        Args:
            system_name: Name of the system
            retries: Number of retry attempts

        Returns:
            Tuple of (x, y, z) or None
        """
        for attempt in range(retries):
            try:
                coords = self._fetch_from_edsm(system_name)
                if coords:
                    return coords
            except Exception as e:
                if attempt < retries - 1:
                    logger.debug(f"EDSM fetch failed for '{system_name}', retrying... (attempt {attempt + 1}/{retries})")
                    time.sleep(0.5)  # Short delay before retry
                else:
                    logger.warning(f"Failed to fetch coordinates for '{system_name}' after {retries} attempts")
        
        return None

    def _get_from_cache(self, system_name: str) -> Optional[Tuple[float, float, float]]:
        """
        Get coordinates from cache.

        Args:
            system_name: Name of the system

        Returns:
            Tuple of (x, y, z) or None
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Check if cached and not expired
                cursor.execute("""
                    SELECT x, y, z, last_updated
                    FROM systems
                    WHERE system_name = ?
                """, (system_name,))
                
                row = cursor.fetchone()
                if not row:
                    return None

                x, y, z, last_updated_str = row
                
                # Check if cache is expired
                if last_updated_str:
                    try:
                        last_updated = datetime.fromisoformat(last_updated_str)
                        if datetime.utcnow() - last_updated > timedelta(days=self.CACHE_EXPIRY_DAYS):
                            logger.debug(f"Cache expired for {system_name}")
                            return None
                    except ValueError:
                        pass

                # All coordinates must be present
                if x is not None and y is not None and z is not None:
                    logger.debug(f"Found {system_name} in cache")
                    return (x, y, z)

                return None

        except Exception as e:
            logger.error(f"Error reading cache for {system_name}: {e}")
            return None

    def _fetch_from_edsm(self, system_name: str) -> Optional[Tuple[float, float, float]]:
        """
        Fetch coordinates from EDSM API.

        Args:
            system_name: Name of the system

        Returns:
            Tuple of (x, y, z) or None
        """
        try:
            logger.debug(f"Fetching coordinates for '{system_name}' from EDSM")
            
            params = {
                "systemName": system_name,
                "showCoordinates": 1,
            }
            
            response = requests.get(
                self.EDSM_API_URL,
                params=params,
                timeout=5,
            )
            response.raise_for_status()
            
            data = response.json()
            logger.debug(f"EDSM response for '{system_name}': {data}")
            
            # EDSM returns either 'id' or 'name' field to indicate the system was found
            if data.get("id") or data.get("name"):
                coords = data.get("coords")
                if coords:
                    x = coords.get("x")
                    y = coords.get("y")
                    z = coords.get("z")
                    
                    if x is not None and y is not None and z is not None:
                        logger.info(f"Found coordinates for {system_name}: ({x}, {y}, {z})")
                        return (x, y, z)
                    else:
                        logger.debug(f"System '{system_name}' found in EDSM but missing coordinate values")
                else:
                    logger.debug(f"System '{system_name}' found in EDSM but no coordinates available")
            else:
                logger.debug(f"System '{system_name}' not found in EDSM")

            return None

        except requests.RequestException as e:
            logger.warning(f"EDSM API error for '{system_name}': {e}")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing EDSM response for '{system_name}': {e}")
            return None

    def _store_in_cache(
        self,
        system_name: str,
        coords: Tuple[float, float, float],
    ) -> None:
        """
        Store coordinates in cache.

        Args:
            system_name: Name of the system
            coords: Tuple of (x, y, z)
        """
        try:
            x, y, z = coords
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO systems (system_name, x, y, z, last_updated)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (system_name, x, y, z))
                
                conn.commit()
                logger.debug(f"Cached coordinates for {system_name}")

        except Exception as e:
            logger.error(f"Error storing coordinates for {system_name}: {e}")

    def clear_cache(self) -> None:
        """Clear the coordinate cache."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM systems")
                conn.commit()
                logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM systems")
                total = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT COUNT(*) FROM systems
                    WHERE last_updated > datetime('now', '-30 days')
                """)
                recent = cursor.fetchone()[0]
                
                return {
                    "total_cached": total,
                    "recent_cached": recent,
                }

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"total_cached": 0, "recent_cached": 0}
