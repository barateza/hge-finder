"""Tests for core manager."""

import pytest

from src.core import HGENotifierManager


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
        assert "hge_signal" in status
        assert "commander_location" in status
        assert "distance" in status
        assert "initialized" in status
        
        manager.stop()

    def test_manager_status_contains_data(self) -> None:
        """Test that status contains expected data."""
        manager = HGENotifierManager()
        manager.start()
        
        status = manager.get_status()
        
        # Should have signal and location data
        assert status["hge_signal"] is not None
        assert status["commander_location"] is not None
        
        # Should be able to calculate distance
        assert status["distance"] is not None
        
        manager.stop()
