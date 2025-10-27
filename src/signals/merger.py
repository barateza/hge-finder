"""Signal merging and aggregation by system and material type.

This module implements signal grouping logic that converts individual EDDN HGE
signals into aggregated SystemSignalGroup objects, similar to edgalaxy.net.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from src.eddn import HGESignal
from src.materials import MaterialInference
from src.signals.models import SystemSignalGroup

logger = logging.getLogger(__name__)


class SimpleSignalMerger:
    """Merge HGE signals by system and material type.
    
    Converts individual EDDN signals into aggregated system groups where each
    group represents all signals for a single system, grouped by material type.
    
    Example workflow:
    1. Signal 1: Tchernobog (Imperial Shielding)
       -> Creates SystemSignalGroup("Tchernobog") with Imperial Shielding material
    2. Signal 2: Tchernobog (Proto Alloys)
       -> Updates existing group, adds Proto Alloys material
    3. Signal 3: Tchernobog (Imperial Shielding, 2 min later)
       -> Updates existing material, increments player_reports count
    
    All signals are stored in memory. Old signals (>40 min) are marked as
    expired and removed during cleanup.
    """
    
    def __init__(self) -> None:
        """Initialize with empty system groups."""
        self.system_groups: Dict[str, SystemSignalGroup] = {}
        self.material_inference = MaterialInference()
        self.logger = logging.getLogger(__name__)
    
    def process_new_signal(self, signal: HGESignal) -> SystemSignalGroup:
        """Process new signal and return updated system group.
        
        Algorithm:
        1. Get or create SystemSignalGroup for signal.system_name
        2. Infer materials from signal (allegiance, state, population)
        3. For each inferred material:
           - Create or update MaterialReport
           - Increment report count if within 5-min window
           - Otherwise reset timestamp and count
        4. Update group metadata (last_report_time, total_reports)
        5. Capture schema version for debugging/analytics
        6. Return updated group
        
        Args:
            signal: HGESignal to process and merge.
        
        Returns:
            Updated SystemSignalGroup after merging the signal.
        """
        system_name = signal.system_name
        timestamp = signal.timestamp
        
        # Get or create system group
        if system_name not in self.system_groups:
            self.logger.debug(f"Creating new SystemSignalGroup for {system_name}")
            group = SystemSignalGroup(
                system_name=system_name,
                allegiance=signal.allegiance,
                state=signal.state,
                coordinates={
                    "x": signal.x or 0.0,
                    "y": signal.y or 0.0,
                    "z": signal.z or 0.0,
                },
                first_report_time=timestamp,
                last_report_time=timestamp,
                total_reports=0,
                population=signal.population,
                government=signal.government,
                schema_version=signal.schema_version,
            )
            self.system_groups[system_name] = group
        else:
            group = self.system_groups[system_name]
            # Update group metadata
            group.last_report_time = timestamp
            
            # Update coordinates if we now have them (fill in missing values)
            if signal.x is not None:
                group.coordinates["x"] = signal.x
            if signal.y is not None:
                group.coordinates["y"] = signal.y
            if signal.z is not None:
                group.coordinates["z"] = signal.z
            
            # Update system info if missing
            group.allegiance = group.allegiance or signal.allegiance
            group.state = group.state or signal.state
            group.population = group.population or signal.population
            group.government = group.government or signal.government
            
            # Update schema_version if signal has it (captures most recent schema)
            if signal.schema_version:
                group.schema_version = signal.schema_version
        
        # Infer materials from signal properties
        inferred_material_infos = self.material_inference.infer_materials(
            allegiance=signal.allegiance,
            state=signal.state,
            population=signal.population,
        )
        
        # Add or update each inferred material
        for material_info in inferred_material_infos:
            group.add_material(material_info.name, timestamp)
        
        # Update total_reports (sum of all material reports)
        group.total_reports = sum(
            report.player_reports for report in group.materials.values()
        )
        
        self.logger.info(
            f"Processed signal for {system_name}: "
            f"({group.total_reports} total reports, {len(group.materials)} materials)"
        )
        
        return group
    
    def cleanup_expired_signals(self) -> int:
        """Remove systems where all signals are likely expired.
        
        A system is considered expired if its first_report_time is more than
        40 minutes in the past. This is based on USS lifetime (~40 minutes).
        
        Note: This removes based on first_report_time, not last_report_time.
        This is correct because:
        - USS spawned 40 min ago = expired (despawned from game)
        - New reports may still come in from old USS, but USS is gone
        - New USS in same system = new group when reported
        
        Returns:
            Number of systems removed.
        """
        now = datetime.now(timezone.utc)
        expired_systems = []
        
        for system_name, group in self.system_groups.items():
            if group.is_likely_expired():
                expired_systems.append(system_name)
        
        for system_name in expired_systems:
            group = self.system_groups.pop(system_name)
            age_minutes = group.first_report_age() / 60
            self.logger.info(
                f"Cleaned up expired system {system_name} "
                f"(age: {age_minutes:.1f}m, reports: {group.total_reports})"
            )
        
        return len(expired_systems)
    
    def get_active_systems(
        self, sort_by: str = "recent", max_results: Optional[int] = None
    ) -> List[SystemSignalGroup]:
        """Get all active (non-expired) system groups.
        
        Performs cleanup first, removing expired systems.
        
        Args:
            sort_by: Sort order: 'recent' (default), 'reports', or 'name'.
                - 'recent': Sorted by last_report_time (most recent first)
                - 'reports': Sorted by total_reports (most reports first)
                - 'name': Sorted alphabetically by system name
            max_results: Optional maximum number of results to return.
        
        Returns:
            List of SystemSignalGroup sorted by chosen metric.
        
        Raises:
            ValueError: If sort_by is not one of the supported values.
        """
        # Clean expired first
        self.cleanup_expired_signals()
        
        # Get active systems
        systems = list(self.system_groups.values())
        
        # Sort
        if sort_by == "recent":
            systems.sort(key=lambda g: g.last_report_time, reverse=True)
        elif sort_by == "reports":
            systems.sort(key=lambda g: g.total_reports, reverse=True)
        elif sort_by == "name":
            systems.sort(key=lambda g: g.system_name)
        else:
            raise ValueError(
                f"Invalid sort_by value: {sort_by}. "
                "Must be 'recent', 'reports', or 'name'."
            )
        
        # Limit results
        if max_results is not None:
            systems = systems[:max_results]
        
        return systems
    
    def get_system_by_name(self, system_name: str) -> Optional[SystemSignalGroup]:
        """Get group for specific system.
        
        Returns the system group regardless of expiration status.
        Use get_active_systems() for filtered results.
        
        Args:
            system_name: Name of the system.
        
        Returns:
            SystemSignalGroup or None if not found.
        """
        return self.system_groups.get(system_name)
    
    def get_systems_by_material(self, material_name: str) -> List[SystemSignalGroup]:
        """Get all systems with a specific material.
        
        Returns only systems containing the specified material.
        Includes both active and expired systems.
        
        Used for filtering UI by material tabs (e.g., show all systems
        with "Imperial Shielding").
        
        Args:
            material_name: Name of the material to filter by.
        
        Returns:
            List of SystemSignalGroup containing that material,
            sorted by report count (descending).
        """
        matching_systems = [
            group
            for group in self.system_groups.values()
            if material_name in group.materials
        ]
        
        # Sort by report count of this specific material (descending)
        matching_systems.sort(
            key=lambda g: g.materials[material_name].player_reports,
            reverse=True
        )
        
        return matching_systems
    
    def get_all_materials(self) -> List[str]:
        """Get list of all unique materials currently in systems.
        
        Returns materials from all systems (active and expired).
        Sorted alphabetically.
        
        Returns:
            List of unique material names.
        """
        materials = set()
        for group in self.system_groups.values():
            materials.update(group.materials.keys())
        
        return sorted(list(materials))
    
    def get_statistics(self) -> dict:
        """Get statistics about current merged signals.
        
        Returns:
            Dictionary with:
            - total_systems: Total system groups
            - active_systems: Non-expired systems
            - total_reports: Sum of all player reports
            - unique_materials: Count of unique materials
        """
        active_systems = self.get_active_systems()
        
        return {
            "total_systems": len(self.system_groups),
            "active_systems": len(active_systems),
            "total_reports": sum(g.total_reports for g in self.system_groups.values()),
            "unique_materials": len(self.get_all_materials()),
        }
    
    def clear_all(self) -> None:
        """Clear all groups (for testing or reset).
        
        WARNING: This deletes all signal data. Use with caution.
        """
        count = len(self.system_groups)
        self.system_groups.clear()
        self.logger.info(f"Cleared {count} system groups")
