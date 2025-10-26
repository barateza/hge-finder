"""
Phase 4B: Distance Calculator Edge Cases and Error Conditions

Tests for DistanceCalculator edge cases: missing coordinates, extreme values,
precision handling, and formatting.
Covers error paths and boundary conditions in src/distance/__init__.py
"""

import pytest
from src.distance import DistanceCalculator


class TestDistanceCalculatorPhase4B:
    """Test distance calculator edge cases and formatting."""

    def test_distance_calculator_basic_distance(self):
        """Test basic distance calculation between two systems."""
        calc = DistanceCalculator()
        
        # Simple case: 3-4-5 triangle
        distance = calc.calculate_distance(0, 0, 0, 3, 4, 0)
        
        assert distance is not None
        assert distance == 5.0

    def test_distance_calculator_negative_coordinates(self):
        """Test distance with negative coordinates."""
        calc = DistanceCalculator()
        
        # Both negative
        distance = calc.calculate_distance(-10, -10, -10, 10, 10, 10)
        
        assert distance is not None
        assert distance > 0

    def test_distance_calculator_same_point(self):
        """Test distance when both points are identical."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(5, 5, 5, 5, 5, 5)
        
        assert distance == 0.0

    def test_distance_calculator_missing_x1(self):
        """Test distance with missing first X coordinate."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(None, 5, 5, 10, 10, 10)
        
        assert distance is None

    def test_distance_calculator_missing_y1(self):
        """Test distance with missing first Y coordinate."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(5, None, 5, 10, 10, 10)
        
        assert distance is None

    def test_distance_calculator_missing_z1(self):
        """Test distance with missing first Z coordinate."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(5, 5, None, 10, 10, 10)
        
        assert distance is None

    def test_distance_calculator_missing_x2(self):
        """Test distance with missing second X coordinate."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(5, 5, 5, None, 10, 10)
        
        assert distance is None

    def test_distance_calculator_missing_y2(self):
        """Test distance with missing second Y coordinate."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(5, 5, 5, 10, None, 10)
        
        assert distance is None

    def test_distance_calculator_missing_z2(self):
        """Test distance with missing second Z coordinate."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(5, 5, 5, 10, 10, None)
        
        assert distance is None

    def test_distance_calculator_all_missing(self):
        """Test distance with all coordinates missing."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(None, None, None, None, None, None)
        
        assert distance is None

    def test_distance_calculator_extreme_positive(self):
        """Test distance with extreme positive coordinates."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(0, 0, 0, 99999.99, 99999.99, 99999.99)
        
        assert distance is not None
        assert distance > 0

    def test_distance_calculator_extreme_negative(self):
        """Test distance with extreme negative coordinates."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(0, 0, 0, -99999.99, -99999.99, -99999.99)
        
        assert distance is not None
        assert distance > 0

    def test_distance_calculator_mixed_extreme(self):
        """Test distance with mixed extreme coordinates."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(-50000, 0, 50000, 50000, 0, -50000)
        
        assert distance is not None
        assert distance > 0

    def test_distance_calculator_precision(self):
        """Test distance calculation precision."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(0, 0, 0, 1, 1, 1)
        
        # Should be sqrt(3) ≈ 1.73
        assert distance is not None
        assert 1.7 < distance < 1.8

    def test_distance_calculator_rounding(self):
        """Test that distance is properly rounded to 2 decimals."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(0, 0, 0, 1.123, 2.456, 3.789)
        
        # Should be rounded to 2 decimals
        assert distance is not None
        decimal_places = len(str(distance).split('.')[-1])
        assert decimal_places <= 2

    def test_distance_calculator_zero_coordinates(self):
        """Test distance with zero coordinates."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(0, 0, 0, 0, 0, 0)
        
        assert distance == 0.0

    def test_distance_calculator_float_precision(self):
        """Test distance with high-precision floats."""
        calc = DistanceCalculator()
        
        distance = calc.calculate_distance(
            1.111111, 2.222222, 3.333333,
            4.444444, 5.555555, 6.666666
        )
        
        assert distance is not None
        assert isinstance(distance, float)

    def test_format_distance_none(self):
        """Test formatting None distance."""
        calc = DistanceCalculator()
        
        formatted = calc.format_distance(None)
        
        assert formatted == "Unknown"

    def test_format_distance_zero(self):
        """Test formatting zero distance."""
        calc = DistanceCalculator()
        
        formatted = calc.format_distance(0.0)
        
        assert formatted == "0.00 ly"

    def test_format_distance_small(self):
        """Test formatting small distance."""
        calc = DistanceCalculator()
        
        formatted = calc.format_distance(1.5)
        
        assert formatted == "1.50 ly"

    def test_format_distance_large(self):
        """Test formatting large distance."""
        calc = DistanceCalculator()
        
        formatted = calc.format_distance(12345.67)
        
        assert formatted == "12345.67 ly"

    def test_format_distance_precision(self):
        """Test formatting maintains 2 decimal precision."""
        calc = DistanceCalculator()
        
        formatted = calc.format_distance(3.14159)
        
        assert formatted == "3.14 ly"

    def test_distance_calculator_symmetry(self):
        """Test that distance is symmetric (A to B = B to A)."""
        calc = DistanceCalculator()
        
        dist_ab = calc.calculate_distance(1, 2, 3, 4, 5, 6)
        dist_ba = calc.calculate_distance(4, 5, 6, 1, 2, 3)
        
        assert dist_ab == dist_ba

    def test_distance_calculator_triangle_inequality(self):
        """Test triangle inequality holds for distances."""
        calc = DistanceCalculator()
        
        # A to B
        dist_ab = calc.calculate_distance(0, 0, 0, 3, 4, 0)
        # B to C
        dist_bc = calc.calculate_distance(3, 4, 0, 3, 4, 5)
        # A to C
        dist_ac = calc.calculate_distance(0, 0, 0, 3, 4, 5)
        
        # Triangle inequality: AC <= AB + BC
        assert dist_ab is not None and dist_bc is not None and dist_ac is not None
        assert dist_ac <= dist_ab + dist_bc

    def test_distance_calculator_one_dimensional(self):
        """Test distance on single axis."""
        calc = DistanceCalculator()
        
        # Only X differs
        distance = calc.calculate_distance(0, 0, 0, 10, 0, 0)
        
        assert distance == 10.0

    def test_distance_calculator_two_dimensional(self):
        """Test distance on two axes."""
        calc = DistanceCalculator()
        
        # X and Y differ
        distance = calc.calculate_distance(0, 0, 0, 3, 4, 0)
        
        assert distance == 5.0

    def test_distance_calculator_three_dimensional(self):
        """Test distance on all three axes."""
        calc = DistanceCalculator()
        
        # All coordinates differ
        distance = calc.calculate_distance(0, 0, 0, 2, 2, 1)
        
        # sqrt(4 + 4 + 1) = sqrt(9) = 3
        assert distance == 3.0

    def test_format_distance_scientific_notation(self):
        """Test formatting with very large numbers."""
        calc = DistanceCalculator()
        
        formatted = calc.format_distance(999999.99)
        
        assert "ly" in formatted
        assert isinstance(formatted, str)

    def test_distance_static_method_callable(self):
        """Test that distance calculation is a static method."""
        # Should be callable without instance
        distance = DistanceCalculator.calculate_distance(0, 0, 0, 3, 4, 0)
        
        assert distance == 5.0

    def test_format_distance_static_method_callable(self):
        """Test that format_distance is a static method."""
        # Should be callable without instance
        formatted = DistanceCalculator.format_distance(5.0)
        
        assert formatted == "5.00 ly"
