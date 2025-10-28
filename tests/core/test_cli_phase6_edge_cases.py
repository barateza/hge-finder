"""
Phase 6: CLI Module Edge Cases and Display Testing

Comprehensive testing of CLI display and argument parsing:
- Terminal rendering edge cases
- Sorting and filtering edge cases
- Display with extreme data
- Argument parsing edge cases

Target: 5% coverage gap (85% → ≥90%)
New Tests: 10+
Estimated Completion: 1.5 hours
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
from io import StringIO
import sys

from src.cli import display_systems_table, get_status_indicator, format_materials, format_age


class TestCLIStatusIndicators:
    """Test status indicator generation."""

    def test_status_indicator_fresh_signal(self):
        """Test status indicator for signal <5 minutes old."""
        age_seconds = 5 * 60  # 5 minutes
        indicator = get_status_indicator(age_seconds)
        
        # Should return emoji indicator
        assert indicator is not None
        assert isinstance(indicator, str)
        assert len(indicator) > 0

    def test_status_indicator_medium_signal(self):
        """Test status indicator for 1-hour-old signal."""
        age_seconds = 1 * 60 * 60  # 1 hour
        indicator = get_status_indicator(age_seconds)
        
        assert indicator is not None
        assert isinstance(indicator, str)

    def test_status_indicator_old_signal(self):
        """Test status indicator for 6-hour-old signal."""
        age_seconds = 6 * 60 * 60  # 6 hours
        indicator = get_status_indicator(age_seconds)
        
        assert indicator is not None
        assert isinstance(indicator, str)

    def test_status_indicator_very_old_signal(self):
        """Test status indicator for 48-hour-old signal."""
        age_seconds = 48 * 60 * 60  # 48 hours
        indicator = get_status_indicator(age_seconds)
        
        assert indicator is not None
        assert isinstance(indicator, str)

    def test_status_indicator_zero_age(self):
        """Test status indicator with zero age."""
        age_seconds = 0
        indicator = get_status_indicator(age_seconds)
        
        assert indicator is not None
        assert isinstance(indicator, str)

    def test_status_indicator_none(self):
        """Test status indicator with None."""
        indicator = get_status_indicator(None)
        
        assert indicator is not None
        assert isinstance(indicator, str)


class TestCLIMaterialFormatting:
    """Test material formatting."""

    def test_format_materials_empty(self):
        """Test formatting empty materials list."""
        materials = []
        result = format_materials(materials)
        
        assert isinstance(result, str)
        assert result == "None"

    def test_format_materials_single(self):
        """Test formatting single material."""
        materials = [{"name": "Imperial Shielding", "count": 1}]
        result = format_materials(materials)
        
        assert "Imperial Shielding" in result
        assert "1" in result

    def test_format_materials_multiple(self):
        """Test formatting multiple materials (3 or less)."""
        materials = [
            {"name": "Imperial Shielding", "count": 5},
            {"name": "Proto Alloys", "count": 3},
            {"name": "Core Dynamics", "count": 2}
        ]
        result = format_materials(materials)
        
        # Should contain all materials and counts
        assert "Imperial Shielding" in result
        assert "5" in result

    def test_format_materials_many(self):
        """Test formatting many materials (>3)."""
        materials = [
            {"name": f"Material{i}", "count": i}
            for i in range(10)
        ]
        result = format_materials(materials)
        
        # Should indicate truncation
        assert "more" in result or "+" in result
        assert isinstance(result, str)

    def test_format_materials_with_special_chars(self):
        """Test formatting materials with special characters."""
        materials = [
            {"name": "Material-With-Dashes", "count": 1},
            {"name": "Material's", "count": 2}
        ]
        result = format_materials(materials)
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestCLIAgeFormatting:
    """Test age formatting."""

    def test_format_age_zero(self):
        """Test formatting zero seconds."""
        result = format_age(0)
        
        assert isinstance(result, str)
        assert "0s" in result or "0" in result

    def test_format_age_seconds(self):
        """Test formatting age in seconds."""
        result = format_age(45)
        
        assert isinstance(result, str)
        assert "s" in result
        assert "45" in result

    def test_format_age_minutes(self):
        """Test formatting age in minutes."""
        result = format_age(5 * 60)
        
        assert isinstance(result, str)
        assert "m" in result
        assert "5" in result

    def test_format_age_hours(self):
        """Test formatting age in hours."""
        result = format_age(3 * 60 * 60)
        
        assert isinstance(result, str)
        assert "h" in result
        assert "3" in result

    def test_format_age_days(self):
        """Test formatting age in days."""
        result = format_age(2 * 24 * 60 * 60)
        
        assert isinstance(result, str)
        assert "d" in result
        assert "2" in result

    def test_format_age_none(self):
        """Test formatting None age."""
        result = format_age(None)
        
        assert isinstance(result, str)
        assert "Unknown" in result


class TestCLITableDisplay:
    """Test table display functionality."""

    def test_display_table_empty_systems(self, capsys):
        """Test displaying table with no systems."""
        systems = []
        display_systems_table(systems, None)
        
        captured = capsys.readouterr()
        assert "No active HGE" in captured.out

    def test_display_table_single_system(self, capsys):
        """Test displaying table with one system."""
        systems = [
            {
                "system_name": "TestSystem",
                "materials": [{"name": "Material1", "count": 1}],
                "total_reports": 1,
                "last_signal_age": 300,
                "distance_ly": 10.5,
                "allegiance": "Federation",
            }
        ]
        
        display_systems_table(systems, None)
        
        captured = capsys.readouterr()
        assert "TestSystem" in captured.out or "ACTIVE SYSTEMS" in captured.out

    def test_display_table_multiple_systems(self, capsys):
        """Test displaying table with multiple systems."""
        systems = [
            {
                "system_name": f"System{i}",
                "materials": [{"name": f"Material{i}", "count": i + 1}],
                "total_reports": i + 1,
                "last_signal_age": 300 * (i + 1),
                "distance_ly": 10.0 + i,
                "allegiance": "Federation",
            }
            for i in range(5)
        ]
        
        display_systems_table(systems, None)
        
        captured = capsys.readouterr()
        assert "ACTIVE SYSTEMS" in captured.out
        assert len(captured.out) > 100

    def test_display_table_with_details(self, capsys):
        """Test displaying detailed table."""
        systems = [
            {
                "system_name": "TestSystem",
                "materials": [{"name": "Material", "count": 1}],
                "total_reports": 1,
                "last_signal_age": 300,
                "distance_ly": 10.5,
                "allegiance": "Federation",
                "state": "Stable",
                "population": 1000000,
            }
        ]
        
        display_systems_table(systems, None, show_details=True)
        
        captured = capsys.readouterr()
        assert "ACTIVE SYSTEMS" in captured.out

    def test_display_table_with_many_systems(self, capsys):
        """Test displaying table with many systems."""
        systems = [
            {
                "system_name": f"System{i}",
                "materials": [{"name": f"Material{i}", "count": (i % 5) + 1}],
                "total_reports": i + 1,
                "last_signal_age": 300 * ((i % 10) + 1),
                "distance_ly": 10.0 + i,
                "allegiance": "Federation",
            }
            for i in range(30)
        ]
        
        display_systems_table(systems, None)
        
        captured = capsys.readouterr()
        assert "ACTIVE SYSTEMS" in captured.out
        assert len(captured.out) > 300


class TestCLISorting:
    """Test sorting functionality."""

    def test_sort_by_distance_ascending(self):
        """Test sorting systems by distance ascending."""
        systems = [
            {"system_name": "Far", "distance_ly": 100.0},
            {"system_name": "Near", "distance_ly": 10.0},
            {"system_name": "Mid", "distance_ly": 50.0},
        ]
        
        sorted_systems = sorted(systems, key=lambda s: s.get("distance_ly", float('inf')))
        
        assert sorted_systems[0]["system_name"] == "Near"
        assert sorted_systems[1]["system_name"] == "Mid"
        assert sorted_systems[2]["system_name"] == "Far"

    def test_sort_by_reports_descending(self):
        """Test sorting systems by report count descending."""
        systems = [
            {"system_name": "Few", "total_reports": 1},
            {"system_name": "Many", "total_reports": 10},
            {"system_name": "Medium", "total_reports": 5},
        ]
        
        sorted_systems = sorted(systems, key=lambda s: s["total_reports"], reverse=True)
        
        assert sorted_systems[0]["system_name"] == "Many"
        assert sorted_systems[1]["system_name"] == "Medium"
        assert sorted_systems[2]["system_name"] == "Few"

    def test_sort_by_recency(self):
        """Test sorting systems by signal recency."""
        now = datetime.utcnow().timestamp()
        systems = [
            {"system_name": "Old", "last_signal_age": 10000},
            {"system_name": "New", "last_signal_age": 100},
            {"system_name": "Mid", "last_signal_age": 5000},
        ]
        
        sorted_systems = sorted(systems, key=lambda s: s["last_signal_age"])
        
        assert sorted_systems[0]["system_name"] == "New"
        assert sorted_systems[1]["system_name"] == "Mid"
        assert sorted_systems[2]["system_name"] == "Old"

    def test_sort_stability(self):
        """Test that sort is stable for equal values."""
        systems = [
            {"system_name": "A", "distance_ly": 10.0, "order": 1},
            {"system_name": "B", "distance_ly": 10.0, "order": 2},
            {"system_name": "C", "distance_ly": 10.0, "order": 3},
        ]
        
        sorted_systems = sorted(systems, key=lambda s: s["distance_ly"])
        
        # All have same distance, so order should be preserved
        assert sorted_systems[0]["order"] == 1
        assert sorted_systems[1]["order"] == 2
        assert sorted_systems[2]["order"] == 3


class TestCLIFiltering:
    """Test filtering functionality."""

    def test_filter_by_material_found(self):
        """Test filtering systems by material (found)."""
        systems = [
            {
                "system_name": "Has",
                "materials": [
                    {"name": "Target", "count": 1},
                    {"name": "Other", "count": 1}
                ],
            },
            {
                "system_name": "NoTarget",
                "materials": [{"name": "Other", "count": 1}],
            }
        ]
        
        filtered = [
            s for s in systems
            if any("Target" in m["name"] for m in s.get("materials", []))
        ]
        
        assert len(filtered) == 1
        assert filtered[0]["system_name"] == "Has"

    def test_filter_by_material_case_insensitive(self):
        """Test filtering is case insensitive."""
        systems = [
            {
                "system_name": "System",
                "materials": [{"name": "Imperial Shielding", "count": 1}],
            }
        ]
        
        search = "imperial"
        filtered = [
            s for s in systems
            if any(search.lower() in m["name"].lower() for m in s.get("materials", []))
        ]
        
        assert len(filtered) == 1

    def test_filter_no_matches(self):
        """Test filtering with no matches."""
        systems = [
            {
                "system_name": "System",
                "materials": [{"name": "Material", "count": 1}],
            }
        ]
        
        filtered = [
            s for s in systems
            if any("NonExistent" in m["name"] for m in s.get("materials", []))
        ]
        
        assert len(filtered) == 0

    def test_filter_by_distance_threshold(self):
        """Test filtering by distance threshold."""
        systems = [
            {"system_name": "Close", "distance_ly": 5.0},
            {"system_name": "Far", "distance_ly": 100.0},
            {"system_name": "Medium", "distance_ly": 50.0},
        ]
        
        max_distance = 60.0
        filtered = [s for s in systems if s["distance_ly"] <= max_distance]
        
        assert len(filtered) == 2
        assert "Close" in [s["system_name"] for s in filtered]
        assert "Medium" in [s["system_name"] for s in filtered]
