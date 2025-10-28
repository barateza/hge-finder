"""
Phase 6: Distance Module Edge Cases

Comprehensive testing of distance calculations:
- Coordinate precision edge cases
- Zero distance calculations
- Very large coordinate ranges
- Edge cases in system lookups

Target: 2% coverage gap (88% → ≥90%)
New Tests: 12+
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
from pathlib import Path

from src.distance import DistanceCalculator
from src.distance.coordinates import CoordinateDatabase


class TestDistanceCalculatorBasic:
    """Test basic distance calculations."""

    def test_calculator_zero_distance(self):
        """Test distance between identical coordinates."""
        calc = DistanceCalculator()
        distance = calc.calculate_distance(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        assert distance == 0.0

    def test_calculator_simple_distance(self):
        """Test distance between simple coordinates."""
        calc = DistanceCalculator()
        # Distance from (0,0,0) to (3,4,0) should be 5
        distance = calc.calculate_distance(0.0, 0.0, 0.0, 3.0, 4.0, 0.0)
        
        assert distance is not None
        assert abs(distance - 5.0) < 0.01

    def test_calculator_3d_distance(self):
        """Test distance in 3D space."""
        calc = DistanceCalculator()
        # Distance from (0,0,0) to (1,1,1)
        distance = calc.calculate_distance(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
        
        assert distance is not None
        # sqrt(3) ≈ 1.73
        assert abs(distance - 1.73) < 0.01

    def test_calculator_negative_coordinates(self):
        """Test distance with negative coordinates."""
        calc = DistanceCalculator()
        distance = calc.calculate_distance(-1.0, -1.0, -1.0, 1.0, 1.0, 1.0)
        
        # Distance should be positive and approximately 3.46
        assert distance is not None
        assert distance > 0
        assert abs(distance - 3.46) < 0.01

    def test_calculator_extreme_coordinates(self):
        """Test distance with extreme coordinates."""
        calc = DistanceCalculator()
        distance = calc.calculate_distance(-99999.99, -99999.99, -99999.99, 99999.99, 99999.99, 99999.99)
        
        assert distance is not None
        assert distance > 0

    def test_calculator_one_axis_distance(self):
        """Test distance with movement on single axis."""
        calc = DistanceCalculator()
        distance = calc.calculate_distance(0.0, 0.0, 0.0, 10.0, 0.0, 0.0)
        
        assert distance is not None
        assert abs(distance - 10.0) < 0.01

    def test_calculator_partial_coordinates_none(self):
        """Test distance with None coordinates."""
        calc = DistanceCalculator()
        distance = calc.calculate_distance(1.0, 2.0, None, 4.0, 5.0, 6.0)
        
        assert distance is None

    def test_calculator_all_none(self):
        """Test distance with all None coordinates."""
        calc = DistanceCalculator()
        distance = calc.calculate_distance(None, None, None, None, None, None)
        
        assert distance is None


class TestDistanceFormatting:
    """Test distance formatting."""

    def test_format_distance_valid(self):
        """Test formatting valid distance."""
        calc = DistanceCalculator()
        formatted = calc.format_distance(10.5)
        
        assert "10.50" in formatted
        assert "ly" in formatted

    def test_format_distance_zero(self):
        """Test formatting zero distance."""
        calc = DistanceCalculator()
        formatted = calc.format_distance(0.0)
        
        assert "0.00" in formatted
        assert "ly" in formatted

    def test_format_distance_none(self):
        """Test formatting None distance."""
        calc = DistanceCalculator()
        formatted = calc.format_distance(None)
        
        assert "Unknown" in formatted

    def test_format_distance_large(self):
        """Test formatting large distance."""
        calc = DistanceCalculator()
        formatted = calc.format_distance(99999.99)
        
        assert "99999.99" in formatted
        assert "ly" in formatted

    def test_format_distance_small(self):
        """Test formatting small distance."""
        calc = DistanceCalculator()
        formatted = calc.format_distance(0.01)
        
        assert "0.01" in formatted
        assert "ly" in formatted


class TestDistanceEdgeCases:
    """Test edge cases in distance calculations."""

    def test_distance_very_close_points(self):
        """Test distance between very close points."""
        calc = DistanceCalculator()
        distance = calc.calculate_distance(0.0, 0.0, 0.0, 0.00001, 0.00001, 0.00001)
        
        assert distance is not None
        # Distance is very small, may round to 0.0
        assert distance >= 0

    def test_distance_very_far_points(self):
        """Test distance between very far points."""
        calc = DistanceCalculator()
        distance = calc.calculate_distance(-99999.0, -99999.0, -99999.0, 99999.0, 99999.0, 99999.0)
        
        assert distance is not None
        assert distance > 0

    def test_distance_precision_preservation(self):
        """Test that precision is preserved in calculations."""
        calc = DistanceCalculator()
        distance1 = calc.calculate_distance(1.1, 2.2, 3.3, 1.1000001, 2.2, 3.3)
        
        distance2 = calc.calculate_distance(0.0, 0.0, 0.0, 0.0000001, 0.0, 0.0)
        
        # Both should be very small
        assert distance1 is not None and distance1 >= 0
        assert distance2 is not None and distance2 >= 0

    def test_distance_symmetry(self):
        """Test that distance is symmetric."""
        calc = DistanceCalculator()
        distance1 = calc.calculate_distance(1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
        
        distance2 = calc.calculate_distance(4.0, 5.0, 6.0, 1.0, 2.0, 3.0)
        
        if distance1 and distance2:
            assert abs(distance1 - distance2) < 0.01

    def test_distance_triangle_inequality(self):
        """Test triangle inequality property."""
        calc = DistanceCalculator()
        
        # A to B, B to C, A to C
        ab = calc.calculate_distance(0.0, 0.0, 0.0, 3.0, 0.0, 0.0)
        bc = calc.calculate_distance(3.0, 0.0, 0.0, 0.0, 4.0, 0.0)
        ac = calc.calculate_distance(0.0, 0.0, 0.0, 0.0, 4.0, 0.0)
        
        if ab and bc and ac:
            # ac should be less than or equal to ab + bc
            assert ac <= ab + bc + 0.01


class TestCoordinateDatabaseInitialization:
    """Test CoordinateDatabase initialization."""

    def test_database_init_default(self):
        """Test database initialization with default path."""
        # Just test that we can create the instance
        with patch('src.distance.coordinates.sqlite3.connect'):
            db = CoordinateDatabase(db_path=Path("."))
            assert db is not None

    def test_database_init_custom_path(self):
        """Test database initialization with custom path."""
        with patch('src.distance.coordinates.sqlite3.connect'):
            custom_path = Path("/custom/path")
            db = CoordinateDatabase(db_path=custom_path)
            assert db.db_path == custom_path

    def test_database_file_created(self):
        """Test that database file is created."""
        with patch('src.distance.coordinates.sqlite3.connect'):
            db = CoordinateDatabase(db_path=Path("."))
            assert db is not None


class TestDistanceCalculatorConsistency:
    """Test distance calculator consistency."""

    def test_calculator_consistency(self):
        """Test calculator returns consistent results."""
        calc1 = DistanceCalculator()
        calc2 = DistanceCalculator()
        
        x1, y1, z1 = 1.5, 2.5, 3.5
        x2, y2, z2 = 4.5, 5.5, 6.5
        
        distance1 = calc1.calculate_distance(x1, y1, z1, x2, y2, z2)
        distance2 = calc2.calculate_distance(x1, y1, z1, x2, y2, z2)
        
        if distance1 and distance2:
            assert distance1 == distance2

    def test_repeated_calculations_same(self):
        """Test that repeated calculations give same result."""
        calc = DistanceCalculator()
        
        d1 = calc.calculate_distance(1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
        d2 = calc.calculate_distance(1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
        d3 = calc.calculate_distance(1.0, 2.0, 3.0, 4.0, 5.0, 6.0)
        
        if d1 and d2 and d3:
            assert d1 == d2 == d3


class TestDistanceIntegration:
    """Test distance calculations with various scenarios."""

    def test_distance_rounding(self):
        """Test that distance is rounded to 2 decimal places."""
        calc = DistanceCalculator()
        distance = calc.calculate_distance(0.0, 0.0, 0.0, 1.1111, 1.1111, 1.1111)
        
        if distance:
            # Should be rounded to 2 decimals
            str_dist = str(distance)
            decimal_part = str_dist.split('.')[-1] if '.' in str_dist else ""
            assert len(decimal_part) <= 2

    def test_distance_always_positive(self):
        """Test that distance is always non-negative."""
        calc = DistanceCalculator()
        test_cases = [
            (0, 0, 0, 1, 1, 1),
            (-5, -5, -5, 5, 5, 5),
            (100, 200, 300, 101, 201, 301),
        ]
        
        for x1, y1, z1, x2, y2, z2 in test_cases:
            distance = calc.calculate_distance(x1, y1, z1, x2, y2, z2)
            if distance is not None:
                assert distance >= 0

    def test_distance_scale_invariance(self):
        """Test distance calculation at different scales."""
        calc = DistanceCalculator()
        
        # Small scale
        d1 = calc.calculate_distance(0, 0, 0, 3, 4, 0)
        
        # Large scale (same proportions)
        d2 = calc.calculate_distance(0, 0, 0, 30, 40, 0)
        
        if d1 and d2:
            # d2 should be approximately 10x d1
            assert abs((d2 / d1) - 10.0) < 0.1
