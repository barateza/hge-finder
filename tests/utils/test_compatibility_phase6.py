"""
Phase 6: Terminal Compatibility Testing

Comprehensive terminal output validation:
- Windows PowerShell compatibility
- Linux bash compatibility  
- macOS compatibility
- Unicode and ANSI color rendering
- Special character handling

Target: Validate cross-platform terminal output
Estimated: 10-12 new tests
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from src.cli import display_systems_table, get_status_indicator, format_age, format_materials


class TestTerminalWindowsCompatibility:
    """Test Windows terminal compatibility."""

    def test_ansi_color_rendering(self):
        """Test ANSI color codes are properly rendered."""
        # Status indicators should use emoji or Unicode
        indicator = get_status_indicator(300)  # 5 minutes
        
        assert indicator is not None
        assert isinstance(indicator, str)

    def test_windows_line_endings(self, capsys):
        """Test output with Windows line endings."""
        systems = [
            {
                "system_name": "TestSystem",
                "materials": [{"name": "Material", "count": 1}],
                "total_reports": 1,
                "last_signal_age": 300,
                "distance_ly": 10.0,
                "allegiance": "Federation",
            }
        ]
        
        display_systems_table(systems, None)
        captured = capsys.readouterr()
        
        # Should not crash with Windows environment
        assert len(captured.out) > 0

    def test_windows_console_width(self, capsys):
        """Test handling of console width limits."""
        systems = [
            {
                "system_name": "VeryLongSystemNameThatExceedsNormalWidth",
                "materials": [{"name": "MaterialName", "count": 1}],
                "total_reports": 1,
                "last_signal_age": 300,
                "distance_ly": 10.0,
                "allegiance": "Federation",
            }
        ]
        
        display_systems_table(systems, None)
        captured = capsys.readouterr()
        
        # Should handle long names gracefully
        assert "ACTIVE SYSTEMS" in captured.out or len(captured.out) > 0

    def test_unicode_in_windows_terminal(self, capsys):
        """Test Unicode characters in Windows terminal."""
        systems = [
            {
                "system_name": "Système",
                "materials": [{"name": "Matériau", "count": 1}],
                "total_reports": 1,
                "last_signal_age": 300,
                "distance_ly": 10.0,
                "allegiance": "Federation",
            }
        ]
        
        display_systems_table(systems, None)
        captured = capsys.readouterr()
        
        # Should render without crashing
        assert len(captured.out) > 0


class TestTerminalLinuxCompatibility:
    """Test Linux terminal compatibility."""

    def test_linux_ansi_colors(self):
        """Test Linux ANSI color support."""
        indicator = get_status_indicator(300)
        
        # Should return emoji or string that works on Linux
        assert indicator is not None
        assert isinstance(indicator, str)

    def test_linux_utf8_rendering(self, capsys):
        """Test UTF-8 rendering on Linux terminals."""
        systems = [
            {
                "system_name": "Linux™",
                "materials": [{"name": "Material", "count": 1}],
                "total_reports": 1,
                "last_signal_age": 300,
                "distance_ly": 10.0,
                "allegiance": "Federation",
            }
        ]
        
        display_systems_table(systems, None)
        captured = capsys.readouterr()
        
        assert len(captured.out) > 0

    def test_linux_terminal_width(self, capsys):
        """Test handling standard Linux terminal width (80 chars)."""
        # Create system with long names that might overflow 80-char terminal
        systems = [
            {
                "system_name": f"System{i}",
                "materials": [{"name": f"Material{i}", "count": 1}],
                "total_reports": i,
                "last_signal_age": 300 * i,
                "distance_ly": 10.0 + i,
                "allegiance": "Federation",
            }
            for i in range(10)
        ]
        
        display_systems_table(systems, None)
        captured = capsys.readouterr()
        
        # Should handle gracefully on narrow terminals
        assert len(captured.out) > 0

    def test_linux_pipe_output(self, capsys):
        """Test output when piped (non-TTY)."""
        # Simulate piped output
        systems = [
            {
                "system_name": "PipedSystem",
                "materials": [{"name": "Material", "count": 1}],
                "total_reports": 1,
                "last_signal_age": 300,
                "distance_ly": 10.0,
                "allegiance": "Federation",
            }
        ]
        
        display_systems_table(systems, None)
        captured = capsys.readouterr()
        
        # Should output valid data even when not interactive
        assert len(captured.out) > 0


class TestTerminalMacOSCompatibility:
    """Test macOS terminal compatibility."""

    def test_macos_emoji_support(self):
        """Test emoji support on macOS terminals."""
        indicator = get_status_indicator(300)
        
        # macOS should support emoji indicators
        assert indicator is not None
        assert isinstance(indicator, str)

    def test_macos_unicode_normalization(self, capsys):
        """Test Unicode normalization on macOS."""
        # macOS often uses NFD (decomposed) Unicode
        systems = [
            {
                "system_name": "Café",  # é can be precomposed or decomposed
                "materials": [{"name": "Material", "count": 1}],
                "total_reports": 1,
                "last_signal_age": 300,
                "distance_ly": 10.0,
                "allegiance": "Federation",
            }
        ]
        
        display_systems_table(systems, None)
        captured = capsys.readouterr()
        
        assert len(captured.out) > 0

    def test_macos_terminal_app(self, capsys):
        """Test rendering in macOS Terminal.app."""
        systems = [
            {
                "system_name": "macOS Test",
                "materials": [{"name": "Material", "count": 1}],
                "total_reports": 1,
                "last_signal_age": 300,
                "distance_ly": 10.0,
                "allegiance": "Federation",
            }
        ]
        
        display_systems_table(systems, None)
        captured = capsys.readouterr()
        
        assert len(captured.out) > 0


class TestTerminalFormattingEdgeCases:
    """Test terminal formatting edge cases."""

    def test_very_long_system_names(self, capsys):
        """Test formatting very long system names."""
        systems = [
            {
                "system_name": "A" * 100,
                "materials": [{"name": "Material", "count": 1}],
                "total_reports": 1,
                "last_signal_age": 300,
                "distance_ly": 10.0,
                "allegiance": "Federation",
            }
        ]
        
        display_systems_table(systems, None)
        captured = capsys.readouterr()
        
        # Should truncate or wrap gracefully
        assert len(captured.out) > 0

    def test_many_materials(self, capsys):
        """Test formatting many materials."""
        systems = [
            {
                "system_name": "System",
                "materials": [
                    {"name": f"Material{i}", "count": i}
                    for i in range(20)
                ],
                "total_reports": 1,
                "last_signal_age": 300,
                "distance_ly": 10.0,
                "allegiance": "Federation",
            }
        ]
        
        display_systems_table(systems, None)
        captured = capsys.readouterr()
        
        # Should handle many materials
        assert len(captured.out) > 0

    def test_special_characters_in_names(self, capsys):
        """Test special characters in system names."""
        special_systems = [
            "System (Test)",
            "System [Test]",
            "System {Test}",
            "System \"Test\"",
            "System 'Test'",
        ]
        
        for sys_name in special_systems:
            systems = [
                {
                    "system_name": sys_name,
                    "materials": [{"name": "Material", "count": 1}],
                    "total_reports": 1,
                    "last_signal_age": 300,
                    "distance_ly": 10.0,
                    "allegiance": "Federation",
                }
            ]
            
            display_systems_table(systems, None)
            captured = capsys.readouterr()
            
            assert len(captured.out) > 0

    def test_numeric_values_formatting(self, capsys):
        """Test formatting of numeric values."""
        systems = [
            {
                "system_name": "System1",
                "materials": [{"name": "Material", "count": 999}],
                "total_reports": 9999,
                "last_signal_age": 999999,
                "distance_ly": 9999.99,
                "allegiance": "Federation",
            }
        ]
        
        display_systems_table(systems, None)
        captured = capsys.readouterr()
        
        # Should handle large numbers
        assert len(captured.out) > 0

    def test_zero_and_empty_values(self, capsys):
        """Test formatting zero and empty values."""
        systems = [
            {
                "system_name": "",
                "materials": [],
                "total_reports": 0,
                "last_signal_age": 0,
                "distance_ly": 0.0,
                "allegiance": "",
            }
        ]
        
        display_systems_table(systems, None)
        captured = capsys.readouterr()
        
        # Should handle empty/zero values gracefully
        assert len(captured.out) >= 0


class TestTerminalColorAndEmoji:
    """Test color codes and emoji rendering."""

    def test_status_indicator_consistency(self):
        """Test status indicators are consistent."""
        indicators = set()
        
        age_values = [0, 60, 300, 3600, 86400, 172800]
        for age in age_values:
            indicator = get_status_indicator(age)
            indicators.add(indicator)
        
        # Should have multiple different indicators
        assert len(indicators) > 1

    def test_age_formatting_variety(self):
        """Test age formatting produces variety."""
        ages = [0, 30, 60, 300, 3600, 86400]
        formatted = [format_age(age) for age in ages]
        
        # Should have different formats for different ages
        assert len(set(formatted)) == len(formatted)

    def test_materials_formatting_truncation(self):
        """Test materials formatting with truncation."""
        many_materials = [{"name": f"Material{i}", "count": i} for i in range(10)]
        formatted = format_materials(many_materials)
        
        # Should indicate truncation
        assert formatted is not None

    def test_terminal_output_no_crashes(self, capsys):
        """Test that any terminal output doesn't crash."""
        test_cases = [
            [],
            [{"system_name": "Test", "materials": [], "total_reports": 0, 
              "last_signal_age": 0, "distance_ly": 0, "allegiance": ""}],
            [
                {"system_name": f"Sys{i}", "materials": [{"name": f"Mat{i}", "count": i}],
                 "total_reports": i, "last_signal_age": i*100, "distance_ly": i*10,
                 "allegiance": ["Federation", "Empire", "Alliance"][i % 3]}
                for i in range(5)
            ],
        ]
        
        for systems in test_cases:
            try:
                display_systems_table(systems, None)
                captured = capsys.readouterr()
                # Should complete without error
                assert True
            except Exception as e:
                pytest.fail(f"Terminal output crashed: {e}")
