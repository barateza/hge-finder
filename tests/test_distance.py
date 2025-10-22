"""Tests for distance calculations."""

import pytest

from src.distance import DistanceCalculator


class TestDistanceCalculator:
    """Test distance calculation functionality."""

    def test_calculate_distance_basic(self) -> None:
        """Test basic distance calculation."""
        # Distance from (0,0,0) to (3,4,0) should be 5
        distance = DistanceCalculator.calculate_distance(
            0, 0, 0,
            3, 4, 0,
        )
        assert distance == 5.0

    def test_calculate_distance_3d(self) -> None:
        """Test 3D distance calculation."""
        # Distance from (1,2,3) to (4,5,6)
        # sqrt((4-1)^2 + (5-2)^2 + (6-3)^2) = sqrt(9 + 9 + 9) = sqrt(27) ≈ 5.20
        distance = DistanceCalculator.calculate_distance(
            1, 2, 3,
            4, 5, 6,
        )
        assert abs(distance - 5.20) < 0.01

    def test_calculate_distance_same_point(self) -> None:
        """Test distance between same point."""
        distance = DistanceCalculator.calculate_distance(
            5, 5, 5,
            5, 5, 5,
        )
        assert distance == 0.0

    def test_calculate_distance_missing_coordinates(self) -> None:
        """Test distance calculation with missing coordinates."""
        distance = DistanceCalculator.calculate_distance(
            0, 0, None,  # Missing z coordinate
            3, 4, 0,
        )
        assert distance is None

    def test_format_distance_valid(self) -> None:
        """Test distance formatting."""
        formatted = DistanceCalculator.format_distance(12.345)
        assert formatted == "12.35 ly"

    def test_format_distance_none(self) -> None:
        """Test distance formatting with None."""
        formatted = DistanceCalculator.format_distance(None)
        assert formatted == "Unknown"
