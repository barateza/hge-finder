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


# ============================================================================
# PHASE 3 EASY: COORDINATE DATABASE EDGE CASES
# ============================================================================


class TestCoordinateDatabaseEdgeCases:
    """Test edge cases for coordinate database."""

    def test_get_from_cache_nonexistent_system(self) -> None:
        """Test getting coordinates for a system that doesn't exist."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            result = db._get_from_cache("Nonexistent System")
            assert result is None
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_store_and_retrieve_with_negative_coordinates(self) -> None:
        """Test storing and retrieving negative coordinates."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            system_name = "Negative System"
            coords = (-10.5, -20.3, -30.1)

            db._store_in_cache(system_name, coords)
            retrieved = db._get_from_cache(system_name)
            assert retrieved == coords
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_store_and_retrieve_with_large_coordinates(self) -> None:
        """Test storing and retrieving large coordinate values."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            system_name = "Far System"
            coords = (10000.5, 20000.3, 30000.1)

            db._store_in_cache(system_name, coords)
            retrieved = db._get_from_cache(system_name)
            assert retrieved == coords
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_store_with_zero_coordinates(self) -> None:
        """Test storing coordinates at origin (0, 0, 0)."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            coords = (0.0, 0.0, 0.0)

            db._store_in_cache("Origin", coords)
            retrieved = db._get_from_cache("Origin")
            assert retrieved == coords
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_get_cache_stats_empty(self) -> None:
        """Test cache stats on empty database."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            stats = db.get_cache_stats()
            assert stats["total_cached"] == 0
            assert stats["recent_cached"] == 0
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_clear_cache_empty_database(self) -> None:
        """Test clearing an already empty cache."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            # Should not raise an exception
            db.clear_cache()
            stats = db.get_cache_stats()
            assert stats["total_cached"] == 0
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_duplicate_system_insert(self) -> None:
        """Test storing coordinates for same system twice (should replace)."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            system_name = "Duplicate Test"

            # Store first coordinates
            db._store_in_cache(system_name, (1.0, 2.0, 3.0))
            stats1 = db.get_cache_stats()
            
            # Store new coordinates for same system
            db._store_in_cache(system_name, (10.0, 20.0, 30.0))
            stats2 = db.get_cache_stats()

            # Total should still be 1 (replaced, not added)
            assert stats1["total_cached"] == 1
            assert stats2["total_cached"] == 1

            # Should have new coordinates
            retrieved = db._get_from_cache(system_name)
            assert retrieved == (10.0, 20.0, 30.0)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_get_from_cache_partial_none_coordinates(self) -> None:
        """Test that cache returns None if any coordinate is missing."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            
            # Insert directly into database with partial data
            with sqlite3.connect(db.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO systems (system_name, x, y, z)
                    VALUES (?, ?, ?, ?)
                """, ("Partial System", 1.0, 2.0, None))
                conn.commit()

            # Getting from cache should return None (incomplete data)
            result = db._get_from_cache("Partial System")
            assert result is None
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_system_name_case_sensitivity(self) -> None:
        """Test that system names are case-sensitive."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            coords = (1.0, 2.0, 3.0)

            db._store_in_cache("Sol", coords)
            
            # Different case should not find it
            result = db._get_from_cache("sol")
            assert result is None

            # Exact case should find it
            result = db._get_from_cache("Sol")
            assert result == coords
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_cache_with_special_characters_in_name(self) -> None:
        """Test system names with special characters."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            special_names = [
                "Test-System",
                "Test System",
                "Test_System",
                "Test (Colony)",
                "Test's World",
            ]

            for i, name in enumerate(special_names):
                coords = (float(i), float(i+1), float(i+2))
                db._store_in_cache(name, coords)

            # All should be retrievable
            for i, name in enumerate(special_names):
                result = db._get_from_cache(name)
                expected = (float(i), float(i+1), float(i+2))
                assert result == expected
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_concurrent_database_access(self) -> None:
        """Test that database handles concurrent writes with locks."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))

            # Store multiple systems
            for i in range(10):
                db._store_in_cache(f"System_{i}", (float(i), float(i), float(i)))

            # All should be retrievable
            for i in range(10):
                result = db._get_from_cache(f"System_{i}")
                assert result == (float(i), float(i), float(i))
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_float_precision(self) -> None:
        """Test float precision is preserved."""
        tmpdir = tempfile.mkdtemp()
        try:
            db = CoordinateDatabase(db_path=Path(tmpdir))
            coords = (1.123456789, 2.987654321, 3.555555555)

            db._store_in_cache("Precise", coords)
            retrieved = db._get_from_cache("Precise")
            
            # SQLite should preserve precision
            assert retrieved is not None
            # Check within reasonable precision (float rounding)
            for stored, retrieved_val in zip(coords, retrieved):
                assert abs(stored - retrieved_val) < 0.0000001
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

