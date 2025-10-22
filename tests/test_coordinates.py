"""Tests for coordinate database."""

import pytest
import sqlite3
import tempfile
import shutil
from pathlib import Path

from src.distance.coordinates import CoordinateDatabase


class TestCoordinateDatabase:
    """Test coordinate database functionality."""

    def test_database_initialization(self):
        """Test database initialization."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            assert db.db_file.exists()
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_store_and_retrieve_coordinates(self):
        """Test storing and retrieving coordinates."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            system_name = "Test System"
            coords = (10.0, 20.0, 30.0)

            # Store coordinates
            db._store_in_cache(system_name, coords)

            # Retrieve coordinates
            retrieved = db._get_from_cache(system_name)
            assert retrieved == coords
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_cache_stats(self):
        """Test cache statistics."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            
            # Initially empty
            stats = db.get_cache_stats()
            assert stats["total_cached"] == 0

            # Add some systems
            db._store_in_cache("System1", (1.0, 2.0, 3.0))
            db._store_in_cache("System2", (4.0, 5.0, 6.0))

            # Check stats
            stats = db.get_cache_stats()
            assert stats["total_cached"] == 2
            assert stats["recent_cached"] == 2
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_clear_cache(self):
        """Test clearing cache."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            
            # Add some systems
            db._store_in_cache("System1", (1.0, 2.0, 3.0))

            # Clear cache
            db.clear_cache()

            # Verify empty
            stats = db.get_cache_stats()
            assert stats["total_cached"] == 0
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_multiple_systems(self):
        """Test handling multiple systems."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            
            systems = {
                "Sol": (0.0, 0.0, 0.0),
                "Sirius": (8.6, 0.0, -2.0),
                "Procyon": (3.5, 2.8, 0.0),
            }

            for system_name, coords in systems.items():
                db._store_in_cache(system_name, coords)

            for system_name, coords in systems.items():
                retrieved = db._get_from_cache(system_name)
                assert retrieved == coords
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

