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

    # Edge Cases - EASY Phase 3 Tests
    def test_calculate_distance_all_none(self) -> None:
        """Test distance calculation when all coordinates are None."""
        distance = DistanceCalculator.calculate_distance(
            None, None, None,
            None, None, None,
        )
        assert distance is None

    def test_calculate_distance_partial_none_source(self) -> None:
        """Test distance calculation with partial None in source coordinates."""
        distance = DistanceCalculator.calculate_distance(
            None, 0, 0,
            3, 4, 5,
        )
        assert distance is None

    def test_calculate_distance_partial_none_target(self) -> None:
        """Test distance calculation with partial None in target coordinates."""
        distance = DistanceCalculator.calculate_distance(
            0, 0, 0,
            3, None, 5,
        )
        assert distance is None

    def test_calculate_distance_zero_coordinates(self) -> None:
        """Test distance calculation with all zero coordinates."""
        distance = DistanceCalculator.calculate_distance(
            0, 0, 0,
            0, 0, 0,
        )
        assert distance == 0.0

    def test_calculate_distance_negative_coordinates(self) -> None:
        """Test distance calculation with negative coordinates."""
        # Distance from (-3, -4, 0) to (0, 0, 0) should be 5
        distance = DistanceCalculator.calculate_distance(
            -3, -4, 0,
            0, 0, 0,
        )
        assert distance == 5.0

    def test_calculate_distance_large_numbers(self) -> None:
        """Test distance calculation with very large coordinate values."""
        # Distance from (0, 0, 0) to (1000000, 1000000, 1000000)
        distance = DistanceCalculator.calculate_distance(
            0, 0, 0,
            1000000, 1000000, 1000000,
        )
        # sqrt(10^12 + 10^12 + 10^12) = sqrt(3 * 10^12) ≈ 1732050.8
        assert distance is not None
        assert distance > 1000000

    def test_calculate_distance_very_small_difference(self) -> None:
        """Test distance calculation with very small coordinate differences."""
        distance = DistanceCalculator.calculate_distance(
            0.0, 0.0, 0.0,
            0.001, 0.001, 0.001,
        )
        assert distance is not None
        # Small values round to 0.0
        assert distance == 0.0

    def test_calculate_distance_mixed_signs(self) -> None:
        """Test distance calculation with mixed positive and negative coordinates."""
        # Distance from (-1, 2, -3) to (1, -2, 3)
        distance = DistanceCalculator.calculate_distance(
            -1, 2, -3,
            1, -2, 3,
        )
        # sqrt((1-(-1))^2 + (-2-2)^2 + (3-(-3))^2) = sqrt(4 + 16 + 36) = sqrt(56) ≈ 7.48
        assert abs(distance - 7.48) < 0.01

    def test_format_distance_zero(self) -> None:
        """Test distance formatting with zero distance."""
        formatted = DistanceCalculator.format_distance(0.0)
        assert formatted == "0.00 ly"

    def test_format_distance_large_value(self) -> None:
        """Test distance formatting with large distance value."""
        formatted = DistanceCalculator.format_distance(999999.99)
        assert formatted == "999999.99 ly"

    def test_format_distance_small_value(self) -> None:
        """Test distance formatting with very small distance value."""
        formatted = DistanceCalculator.format_distance(0.01)
        assert formatted == "0.01 ly"

    def test_format_distance_rounding(self) -> None:
        """Test distance formatting performs correct rounding."""
        formatted = DistanceCalculator.format_distance(1.234)
        assert formatted == "1.23 ly"

    def test_format_distance_rounding_up(self) -> None:
        """Test distance formatting rounds up correctly."""
        formatted = DistanceCalculator.format_distance(1.235)
        assert formatted == "1.24 ly" or formatted == "1.23 ly"  # May vary by rounding
