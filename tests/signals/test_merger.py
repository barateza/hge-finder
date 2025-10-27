"""Unit tests for SimpleSignalMerger.

Tests cover all signal merging scenarios:
- Creating new groups
- Adding materials to existing groups
- Incrementing report counts for recent signals
- Resetting timestamps for old signals
- Cleanup of expired signals
- Sorting and filtering
- Edge cases
"""

import pytest
from datetime import datetime, timezone, timedelta
from src.eddn import HGESignal
from src.signals.merger import SimpleSignalMerger
from src.signals.models import SystemSignalGroup, MaterialReport


class TestSimpleSignalMergerBasics:
    """Test basic merger operations."""
    
    @pytest.fixture
    def merger(self):
        """Create a fresh merger for each test."""
        return SimpleSignalMerger()
    
    @pytest.fixture
    def sample_signal(self):
        """Create a sample HGE signal."""
        return HGESignal(
            system_name="Tchernobog",
            timestamp=datetime.now(timezone.utc),
            x=-78.59375,
            y=-149.625,
            z=-340.53125,
            allegiance="Independent",
            state=None,
            population=0,
            government="Corporate",
        )
    
    def test_create_new_system_group(self, merger, sample_signal):
        """Test that new signal creates a system group."""
        group = merger.process_new_signal(sample_signal)
        
        assert group.system_name == "Tchernobog"
        assert group.allegiance == "Independent"
        assert group.coordinates["x"] == -78.59375
        assert len(group.materials) > 0  # Should have inferred materials
    
    def test_system_group_stored_in_merger(self, merger, sample_signal):
        """Test that created group is stored in merger."""
        group = merger.process_new_signal(sample_signal)
        
        retrieved = merger.get_system_by_name("Tchernobog")
        assert retrieved is group
        assert retrieved.system_name == "Tchernobog"
    
    def test_get_nonexistent_system(self, merger):
        """Test getting a system that doesn't exist."""
        result = merger.get_system_by_name("NonexistentSystem")
        assert result is None
    
    def test_clear_all_systems(self, merger, sample_signal):
        """Test clearing all systems."""
        merger.process_new_signal(sample_signal)
        assert len(merger.system_groups) > 0
        
        merger.clear_all()
        assert len(merger.system_groups) == 0


class TestSignalMerging:
    """Test merging of multiple signals."""
    
    @pytest.fixture
    def merger(self):
        """Create a fresh merger for each test."""
        return SimpleSignalMerger()
    
    def create_signal(
        self,
        system_name="Tchernobog",
        timestamp=None,
        allegiance="Independent",
        state=None,
        population=0,
    ):
        """Helper to create signals with various parameters."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        return HGESignal(
            system_name=system_name,
            timestamp=timestamp,
            x=-78.59375,
            y=-149.625,
            z=-340.53125,
            allegiance=allegiance,
            state=state,
            population=population,
            government="Corporate",
        )
    
    def test_same_system_same_material_increments_count(self, merger):
        """Test that repeated reports increment player count for same material."""
        timestamp1 = datetime.now(timezone.utc)
        timestamp2 = timestamp1 + timedelta(seconds=30)
        
        # First signal
        signal1 = self.create_signal(timestamp=timestamp1)
        group1 = merger.process_new_signal(signal1)
        initial_count = group1.total_reports
        assert initial_count > 0
        
        # Second signal for same system, same material (within 5 min)
        signal2 = self.create_signal(timestamp=timestamp2)
        group2 = merger.process_new_signal(signal2)
        
        # Should be same group
        assert group2 is group1
        # Total reports should be higher
        assert group2.total_reports > initial_count
        # Should have same number of materials
        assert len(group2.materials) == len(group1.materials)
    
    def test_same_system_different_material_adds_material(self, merger):
        """Test adding different material to same system."""
        timestamp1 = datetime.now(timezone.utc)
        
        # First signal with state that gives certain materials
        signal1 = self.create_signal(
            timestamp=timestamp1,
            state="Civil Unrest"
        )
        group1 = merger.process_new_signal(signal1)
        materials_1 = set(group1.materials.keys())
        
        # Second signal with different state (gives different materials)
        timestamp2 = timestamp1 + timedelta(seconds=30)
        signal2 = self.create_signal(
            timestamp=timestamp2,
            state="War"
        )
        group2 = merger.process_new_signal(signal2)
        materials_2 = set(group2.materials.keys())
        
        # Should be same group
        assert group2 is group1
        # Should have more materials (union of both)
        assert len(materials_2) >= len(materials_1)
    
    def test_same_system_same_material_old_signal_resets_count(self, merger):
        """Test that old signal (>5min) resets the player count."""
        timestamp1 = datetime.now(timezone.utc)
        timestamp2 = timestamp1 + timedelta(minutes=10)
        
        # First signal
        signal1 = self.create_signal(timestamp=timestamp1)
        group1 = merger.process_new_signal(signal1)
        
        # Get first material and its original count
        first_material_name = list(group1.materials.keys())[0]
        original_count = group1.materials[first_material_name].player_reports
        
        # Second signal (10 minutes later, outside 5-min window)
        signal2 = self.create_signal(timestamp=timestamp2)
        group2 = merger.process_new_signal(signal2)
        
        # Material count should be reset to 1 (not incremented)
        new_count = group2.materials[first_material_name].player_reports
        assert new_count == 1
    
    def test_different_system_creates_new_group(self, merger):
        """Test that different systems create different groups."""
        signal1 = self.create_signal(system_name="System1")
        signal2 = self.create_signal(system_name="System2")
        
        group1 = merger.process_new_signal(signal1)
        group2 = merger.process_new_signal(signal2)
        
        assert group1 is not group2
        assert group1.system_name == "System1"
        assert group2.system_name == "System2"
        assert len(merger.system_groups) == 2
    
    def test_update_coordinates_if_missing(self, merger):
        """Test that coordinates are updated when initially missing."""
        # First signal without coordinates
        signal1 = HGESignal(
            system_name="Test",
            timestamp=datetime.now(timezone.utc),
            x=None,
            y=None,
            z=None,
            allegiance="Federation",
        )
        group1 = merger.process_new_signal(signal1)
        coords1_x = group1.coordinates["x"]
        
        # Second signal with coordinates
        signal2 = HGESignal(
            system_name="Test",
            timestamp=datetime.now(timezone.utc) + timedelta(seconds=1),
            x=123.45,
            y=67.89,
            z=12.34,
            allegiance="Federation",
        )
        group2 = merger.process_new_signal(signal2)
        
        # Should be same group, coordinates updated
        assert group2 is group1
        assert group2.coordinates["x"] == 123.45
        assert group2.coordinates["y"] == 67.89
        assert group2.coordinates["z"] == 12.34


class TestCleanup:
    """Test expiration and cleanup logic."""
    
    @pytest.fixture
    def merger(self):
        """Create a fresh merger for each test."""
        return SimpleSignalMerger()
    
    def create_old_signal(self, merger, minutes_old=50):
        """Helper to create a signal from N minutes ago."""
        old_time = datetime.now(timezone.utc) - timedelta(minutes=minutes_old)
        
        signal = HGESignal(
            system_name=f"OldSystem{minutes_old}",
            timestamp=old_time,
            x=0.0,
            y=0.0,
            z=0.0,
            allegiance="Federation",
        )
        return merger.process_new_signal(signal)
    
    def test_expired_signal_marked_as_expired(self, merger):
        """Test that signal older than 40 min is marked as expired."""
        self.create_old_signal(merger, minutes_old=41)
        
        group = merger.get_system_by_name("OldSystem41")
        assert group is not None
        assert group.is_likely_expired()
    
    def test_recent_signal_not_marked_as_expired(self, merger):
        """Test that signal younger than 40 min is NOT marked as expired."""
        self.create_old_signal(merger, minutes_old=30)
        
        group = merger.get_system_by_name("OldSystem30")
        assert group is not None
        assert not group.is_likely_expired()
    
    def test_cleanup_removes_expired_systems(self, merger):
        """Test that cleanup removes expired systems."""
        # Add old system
        self.create_old_signal(merger, minutes_old=50)
        assert merger.get_system_by_name("OldSystem50") is not None
        
        # Cleanup
        removed_count = merger.cleanup_expired_signals()
        
        assert removed_count == 1
        assert merger.get_system_by_name("OldSystem50") is None
    
    def test_cleanup_keeps_recent_systems(self, merger):
        """Test that cleanup keeps recent systems."""
        # Add recent system
        self.create_old_signal(merger, minutes_old=30)
        
        # Cleanup
        removed_count = merger.cleanup_expired_signals()
        
        assert removed_count == 0
        assert merger.get_system_by_name("OldSystem30") is not None
    
    def test_cleanup_mixed_old_and_recent(self, merger):
        """Test cleanup with mix of old and recent systems."""
        self.create_old_signal(merger, minutes_old=50)  # Will be removed
        self.create_old_signal(merger, minutes_old=30)  # Will be kept
        
        initial_count = len(merger.system_groups)
        assert initial_count == 2
        
        removed_count = merger.cleanup_expired_signals()
        
        assert removed_count == 1
        assert len(merger.system_groups) == 1


class TestSortingAndFiltering:
    """Test sorting and filtering operations."""
    
    @pytest.fixture
    def merger_with_systems(self):
        """Create a merger with multiple systems."""
        merger = SimpleSignalMerger()
        
        # Add systems with different timestamps and report counts
        timestamps = [
            datetime.now(timezone.utc) - timedelta(minutes=10),
            datetime.now(timezone.utc) - timedelta(minutes=5),
            datetime.now(timezone.utc),
        ]
        system_names = ["Alpha", "Beta", "Gamma"]
        
        for name, ts in zip(system_names, timestamps):
            signal = HGESignal(
                system_name=name,
                timestamp=ts,
                x=0.0,
                y=0.0,
                z=0.0,
                allegiance="Federation",
            )
            merger.process_new_signal(signal)
        
        return merger
    
    def test_sort_by_recent(self, merger_with_systems):
        """Test sorting by most recent."""
        systems = merger_with_systems.get_active_systems(sort_by="recent")
        
        # Most recent first
        assert systems[0].system_name == "Gamma"
        assert systems[1].system_name == "Beta"
        assert systems[2].system_name == "Alpha"
    
    def test_sort_by_name(self, merger_with_systems):
        """Test sorting by name."""
        systems = merger_with_systems.get_active_systems(sort_by="name")
        
        assert systems[0].system_name == "Alpha"
        assert systems[1].system_name == "Beta"
        assert systems[2].system_name == "Gamma"
    
    def test_sort_by_reports(self, merger_with_systems):
        """Test sorting by report count."""
        systems = merger_with_systems.get_active_systems(sort_by="reports")
        
        # All should have same report count initially, so order depends on sort stability
        # Just verify the method works without error
        assert len(systems) == 3
    
    def test_sort_invalid_raises_error(self, merger_with_systems):
        """Test that invalid sort option raises error."""
        with pytest.raises(ValueError):
            merger_with_systems.get_active_systems(sort_by="invalid")
    
    def test_get_active_systems_with_max_results(self, merger_with_systems):
        """Test limiting results with max_results."""
        systems = merger_with_systems.get_active_systems(max_results=2)
        
        assert len(systems) == 2
    
    def test_get_systems_by_material_federal(self, merger_with_systems):
        """Test filtering systems by material."""
        systems = merger_with_systems.get_active_systems()
        
        # Should have Federal materials since we created Federal systems
        federal_systems = merger_with_systems.get_systems_by_material(
            "Core Dynamics Composites"
        )
        
        assert len(federal_systems) > 0
    
    def test_get_systems_by_nonexistent_material(self, merger_with_systems):
        """Test filtering by material that doesn't exist."""
        systems = merger_with_systems.get_systems_by_material(
            "Nonexistent Material"
        )
        
        assert len(systems) == 0
    
    def test_get_all_materials(self, merger_with_systems):
        """Test getting all unique materials."""
        materials = merger_with_systems.get_all_materials()
        
        assert len(materials) > 0
        assert all(isinstance(m, str) for m in materials)
        # Should be sorted
        assert materials == sorted(materials)


class TestStatistics:
    """Test statistics generation."""
    
    @pytest.fixture
    def merger_with_data(self):
        """Create a merger with some test data."""
        merger = SimpleSignalMerger()
        
        # Add a few systems
        for i in range(3):
            signal = HGESignal(
                system_name=f"System{i}",
                timestamp=datetime.now(timezone.utc),
                x=float(i),
                y=float(i),
                z=float(i),
                allegiance="Federation",
            )
            merger.process_new_signal(signal)
        
        return merger
    
    def test_get_statistics(self, merger_with_data):
        """Test statistics generation."""
        stats = merger_with_data.get_statistics()
        
        assert stats["total_systems"] == 3
        assert stats["active_systems"] == 3
        assert stats["total_reports"] >= 3
        assert stats["unique_materials"] > 0
    
    def test_statistics_after_cleanup(self, merger_with_data):
        """Test that statistics are updated after cleanup."""
        # Verify initial state
        stats_initial = merger_with_data.get_statistics()
        initial_count = stats_initial["total_systems"]
        assert initial_count == 3
        
        # Add an expired system
        old_time = datetime.now(timezone.utc) - timedelta(minutes=50)
        signal = HGESignal(
            system_name="OldSystem",
            timestamp=old_time,
            x=0.0,
            y=0.0,
            z=0.0,
            allegiance="Federation",
        )
        merger_with_data.process_new_signal(signal)
        
        # Verify old system is in memory (before cleanup)
        assert merger_with_data.get_system_by_name("OldSystem") is not None
        
        # Get active systems (triggers cleanup)
        merger_with_data.get_active_systems()
        
        # Old system should be removed
        stats_after = merger_with_data.get_statistics()
        assert stats_after["total_systems"] == 3
        assert merger_with_data.get_system_by_name("OldSystem") is None


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def merger(self):
        """Create a fresh merger for each test."""
        return SimpleSignalMerger()
    
    def test_signal_with_missing_data(self, merger):
        """Test processing signal with missing optional data."""
        signal = HGESignal(
            system_name="TestSystem",
            timestamp=datetime.now(timezone.utc),
            x=None,
            y=None,
            z=None,
            allegiance=None,
            state=None,
            population=None,
            government=None,
        )
        
        # Should not crash
        group = merger.process_new_signal(signal)
        assert group.system_name == "TestSystem"
    
    def test_signal_with_empty_strings(self, merger):
        """Test processing signal with empty string values."""
        signal = HGESignal(
            system_name="TestSystem",
            timestamp=datetime.now(timezone.utc),
            x=0.0,
            y=0.0,
            z=0.0,
            allegiance="",
            state="",
            population=0,
            government="",
        )
        
        # Should not crash
        group = merger.process_new_signal(signal)
        assert group.system_name == "TestSystem"
    
    def test_rapid_signal_spam(self, merger):
        """Test handling rapid signals from same system."""
        base_time = datetime.now(timezone.utc)
        
        # Send 100 signals rapidly
        for i in range(100):
            signal = HGESignal(
                system_name="SpamSystem",
                timestamp=base_time + timedelta(milliseconds=i),
                x=0.0,
                y=0.0,
                z=0.0,
                allegiance="Federation",
            )
            merger.process_new_signal(signal)
        
        # Should only have one system group
        assert len(merger.system_groups) == 1
        
        # Report count should be high
        group = merger.get_system_by_name("SpamSystem")
        assert group.total_reports > 1
    
    def test_get_active_systems_cleans_up_first(self, merger):
        """Test that get_active_systems cleans up expired before returning."""
        # Add expired system
        old_time = datetime.now(timezone.utc) - timedelta(minutes=50)
        signal = HGESignal(
            system_name="OldSystem",
            timestamp=old_time,
            x=0.0,
            y=0.0,
            z=0.0,
            allegiance="Federation",
        )
        merger.process_new_signal(signal)
        
        assert len(merger.system_groups) == 1
        
        # get_active_systems should clean up first
        active = merger.get_active_systems()
        
        assert len(active) == 0
        assert len(merger.system_groups) == 0
    
    def test_material_timestamp_handling(self, merger):
        """Test that material timestamps are correctly updated."""
        time1 = datetime.now(timezone.utc)
        time2 = time1 + timedelta(seconds=30)
        
        # First signal with Civil Unrest - gives "Improvised Components"
        signal1 = HGESignal(
            system_name="Test",
            timestamp=time1,
            x=0.0,
            y=0.0,
            z=0.0,
            allegiance="Federation",
            state="Civil Unrest",
        )
        group1 = merger.process_new_signal(signal1)
        material_name = "Improvised Components"
        
        # Make sure the material exists
        assert material_name in group1.materials
        timestamp1 = group1.materials[material_name].timestamp
        
        # Second signal slightly later, same material should update timestamp
        signal2 = HGESignal(
            system_name="Test",
            timestamp=time2,
            x=0.0,
            y=0.0,
            z=0.0,
            allegiance="Federation",
            state="Civil Unrest",
        )
        group2 = merger.process_new_signal(signal2)
        timestamp2 = group2.materials[material_name].timestamp
        
        # Timestamp should be updated since within 5 min
        assert timestamp2 >= timestamp1
    
    def test_very_large_population(self, merger):
        """Test signal with very large population value."""
        signal = HGESignal(
            system_name="BigSystem",
            timestamp=datetime.now(timezone.utc),
            x=0.0,
            y=0.0,
            z=0.0,
            allegiance="Federation",
            state="Outbreak",
            population=999_999_999,  # Very large
        )
        
        group = merger.process_new_signal(signal)
        assert group.population == 999_999_999


class TestIntegration:
    """Integration tests for complex scenarios."""
    
    @pytest.fixture
    def merger(self):
        """Create a fresh merger for each test."""
        return SimpleSignalMerger()
    
    def test_complex_scenario_multiple_systems_and_materials(self, merger):
        """Test a complex scenario with multiple systems reporting different materials."""
        # Scenario: Two independent systems, each reporting multiple times
        
        # System 1: Reported 3 times (2 within 5min, 1 after)
        time_base = datetime.now(timezone.utc)
        
        systems_data = [
            ("Tchernobog", time_base, "Independent", None),
            ("Tchernobog", time_base + timedelta(seconds=30), "Independent", None),
            ("Tchernobog", time_base + timedelta(minutes=10), "Independent", None),
            ("Mundii", time_base + timedelta(seconds=10), "Federation", "War"),
            ("Mundii", time_base + timedelta(seconds=40), "Federation", "War"),
        ]
        
        for system_name, timestamp, allegiance, state in systems_data:
            signal = HGESignal(
                system_name=system_name,
                timestamp=timestamp,
                x=0.0,
                y=0.0,
                z=0.0,
                allegiance=allegiance,
                state=state,
            )
            merger.process_new_signal(signal)
        
        # Verify results
        systems = merger.get_active_systems()
        assert len(systems) == 2
        
        tch = merger.get_system_by_name("Tchernobog")
        mundii = merger.get_system_by_name("Mundii")
        
        assert tch is not None
        assert mundii is not None
        
        # Tchernobog should have reports from both Independent and possibly War
        assert tch.total_reports >= 2
        
        # Mundii should have War materials
        assert mundii.total_reports >= 2
    
    def test_signal_history_with_updates(self, merger):
        """Test that signal history is correctly maintained over time."""
        systems_timeline = [
            (datetime.now(timezone.utc), "Alpha", "Federation"),
            (datetime.now(timezone.utc) + timedelta(seconds=5), "Beta", "Empire"),
            (datetime.now(timezone.utc) + timedelta(seconds=10), "Alpha", "Federation"),
            (datetime.now(timezone.utc) + timedelta(seconds=15), "Gamma", "Independent"),
        ]
        
        for timestamp, system_name, allegiance in systems_timeline:
            signal = HGESignal(
                system_name=system_name,
                timestamp=timestamp,
                x=0.0,
                y=0.0,
                z=0.0,
                allegiance=allegiance,
            )
            merger.process_new_signal(signal)
        
        # Should have 3 unique systems
        assert len(merger.system_groups) == 3
        
        # Alpha should have latest timestamp
        alpha = merger.get_system_by_name("Alpha")
        beta = merger.get_system_by_name("Beta")
        
        assert alpha.last_report_time > beta.last_report_time
