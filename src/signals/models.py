"""Data models for signal grouping and aggregation.

This module defines the core data structures for aggregating HGE signals:
- MaterialReport: Represents a single material type report in a system
- SystemSignalGroup: Aggregates all materials in one system
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


@dataclass
class MaterialReport:
    """Single report of a material type in a system.
    
    Represents when a specific material was detected in a system,
    with a count of how many players reported it in the same time window.
    """
    
    material_name: str
    """Name of the material (e.g., 'Imperial Shielding')."""
    
    timestamp: datetime
    """When this material was last reported."""
    
    player_reports: int = 1
    """How many players reported this material in the same time window.
    
    Incremented when multiple players report the same material within
    ~5 minutes (likely the same USS). Otherwise reset with new timestamp.
    """
    
    def age_seconds(self) -> int:
        """Get age of report in seconds."""
        now = datetime.now(timezone.utc)
        ts = self.timestamp
        
        # Handle both naive and timezone-aware datetimes
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        
        return int((now - ts).total_seconds())
    
    def age_human_readable(self) -> str:
        """Get human-readable age: '57 mins ago', '2h ago', etc."""
        age = self.age_seconds()
        
        if age < 60:
            return f"{age}s ago"
        elif age < 3600:
            return f"{age // 60}m ago"
        elif age < 86400:
            return f"{age // 3600}h ago"
        else:
            return f"{age // 86400}d ago"
    
    def is_recent(self, minutes: int = 5) -> bool:
        """Check if this report is recent (within N minutes).
        
        Used to determine if a new report for the same material is
        from the same USS (recent) or a different USS (old).
        
        Args:
            minutes: Threshold in minutes (default 5).
        
        Returns:
            True if age < N minutes.
        """
        return self.age_seconds() < (minutes * 60)


@dataclass
class SystemSignalGroup:
    """Aggregated signals for a single star system.
    
    Represents all HGE reports in one system, grouped by material type.
    This is the core unit of display - one group per system shows:
    - What materials spawn there (with player confirmation counts)
    - When the system was last reported (informational only)
    - When it's likely to expire (based on first_report_time + 40 min)
    
    CRITICAL: "Last Signal" time ≠ USS expiration!
    - "Last Signal: 5 hours ago" = last EDDN report timestamp
    - USS may STILL BE VALID even if last report was hours ago
    - USS expires based on first_report_time + 40 minutes
    - Lack of recent reports just means low player traffic
    """
    
    system_name: str
    """Name of the star system (e.g., 'Tchernobog')."""
    
    allegiance: Optional[str]
    """System allegiance: Federation, Empire, Alliance, Independent, None."""
    
    state: Optional[str]
    """Current system state: War, Civil Unrest, Boom, None, etc."""
    
    coordinates: Dict[str, float]
    """System coordinates: {'x': float, 'y': float, 'z': float}."""
    
    materials: Dict[str, MaterialReport] = field(default_factory=dict)
    """Map of material_name -> MaterialReport.
    
    Each entry represents reports of that material in this system.
    Example:
        {
            'Imperial Shielding': MaterialReport(...),
            'Proto Alloys & Heat Radiators': MaterialReport(...)
        }
    """
    
    first_report_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    """When the first signal for this system was received.
    
    Used to calculate USS expiration: first_report_time + 40 minutes.
    NOT the same as last_report_time (which can be updated as reports come in).
    """
    
    last_report_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    """When the most recent signal for this system was received.
    
    Used for display as "Last signal: X ago". Updated each time a signal
    for this system arrives, regardless of material.
    """
    
    total_reports: int = 0
    """Total number of signal reports for this system.
    
    Sum of all player_reports across all materials.
    Used for confidence scoring.
    """
    
    population: Optional[int] = None
    """System population (from EDSM).
    
    Note: EDSM data may be up to 24 hours stale (updated post-tick).
    This only affects material inference accuracy after server tick events.
    See materials.py MaterialInference for details on how population is used.
    """
    
    government: Optional[str] = None
    """System government type (from EDSM).
    
    Note: EDSM data may be up to 24 hours stale (updated post-tick).
    """
    
    allegiance_source: str = "edsm"
    """Source of allegiance data: 'edsm' or 'eddn'.
    
    Useful for debugging data freshness issues. EDSM-sourced allegiance
    may be up to 24 hours stale post-tick; EDDN-sourced is real-time.
    """
    
    schema_version: Optional[str] = None
    """EDDN schema version that produced this group.
    
    Captured from HGESignal.schema_version for debugging/analytics.
    Useful for tracking which message schemas are most common.
    Example: "FSSSignalDiscovered.json"
    """
    
    @property
    def material_summary(self) -> List[Tuple[str, int]]:
        """Returns [(material_name, count), ...] sorted by count descending.
        
        Used for display: [('Imperial Shielding', 13), ('Proto Alloys', 10)]
        
        Returns:
            List of (material_name, player_report_count) tuples, sorted
            by count in descending order.
        """
        return sorted(
            [(name, report.player_reports) for name, report in self.materials.items()],
            key=lambda x: x[1],
            reverse=True
        )
    
    @property
    def last_signal_age(self) -> str:
        """Returns age of most recent EDDN report: '57 mins ago', '5h ago', etc.
        
        CRITICAL: This is NOT the USS expiration timer!
        
        What this shows:
        - When the last player reported seeing HGE in this system to EDDN
        - "5 hours ago" = last report timestamp
        
        What this DOESN'T show:
        - USS may still be valid even with old "last signal" time
        - USS expiration is based on when it first spawned + 40 minutes
        - No recent reports just means low player traffic to EDDN
        
        Use case:
        - High confidence if report is recent (< 30 min)
        - Old reports still valuable, just less player confirmation
        - Safe to visit system even with "5 hours ago" if within 40 min of first spawn
        
        Returns:
            Human-readable age string (e.g., '57 mins ago').
        """
        now = datetime.now(timezone.utc)
        ts = self.last_report_time
        
        # Handle both naive and timezone-aware datetimes
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        
        age = int((now - ts).total_seconds())
        
        if age < 60:
            return f"{age}s ago"
        elif age < 3600:
            return f"{age // 60}m ago"
        elif age < 86400:
            return f"{age // 3600}h ago"
        else:
            return f"{age // 86400}d ago"
    
    def first_report_age(self) -> int:
        """Get age of first report in seconds.
        
        Used to calculate USS expiration and determine if system should
        be cleaned up from active list.
        
        Returns:
            Age in seconds.
        """
        now = datetime.now(timezone.utc)
        ts = self.first_report_time
        
        # Handle both naive and timezone-aware datetimes
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        
        return int((now - ts).total_seconds())
    
    def is_likely_expired(self) -> bool:
        """Check if USS is probably expired (past 40-minute lifetime).
        
        IMPORTANT: This is NOT based on "last report time"!
        
        USS lifetime: ~40 minutes from spawn (first_report_time)
        - first_report_time = when first player reported this system
        - USS expires: first_report_time + 40 minutes
        - After expiration, USS despawns from game
        
        Why we use first_report_time (not last_report_time):
        - Multiple USS can spawn in same system throughout the day
        - We track each group independently
        - When USS #1 expires (40 min after first report):
          - May still see reports from players going there
          - But USS has despawned, those are stale/old USS
        
        Strategy:
        - If first_report_time > 40 min old → likely expired
        - Remove from active display (cleanup)
        - Archive to history if needed
        - New reports in same system → create new group
        
        Returns:
            True if oldest report > 40 minutes old.
        """
        age_seconds = self.first_report_age()
        USS_LIFETIME_SECONDS = 40 * 60  # 40 minutes
        return age_seconds > USS_LIFETIME_SECONDS
    
    def confidence_percentage(self) -> int:
        """Returns confidence score 0-100 based on report count.
        
        More player confirmations = higher confidence.
        
        Formula: 50 + (total_reports * 3), capped at 100
        - 1 report = 53%
        - 5 reports = 65%
        - 13 reports = 89%
        - 17+ reports = 100%
        
        Returns:
            Confidence score 0-100.
        """
        return min(100, 50 + (self.total_reports * 3))
    
    def add_material(self, material_name: str, timestamp: datetime) -> None:
        """Add or update a material report for this system.
        
        If material doesn't exist, creates new MaterialReport.
        If material exists and timestamp is recent (within 5 min), increments count.
        If material exists but timestamp is old, resets with new timestamp.
        
        Args:
            material_name: Name of the material.
            timestamp: When it was reported.
        """
        if material_name not in self.materials:
            # New material for this system
            self.materials[material_name] = MaterialReport(
                material_name=material_name,
                timestamp=timestamp,
                player_reports=1,
            )
        else:
            existing = self.materials[material_name]
            time_diff = (timestamp - existing.timestamp).total_seconds()
            
            # If within 5 minutes, likely same USS - increment count
            if time_diff < 300:  # 5 minutes
                existing.player_reports += 1
            else:
                # Different USS (5+ minutes old) - reset with new timestamp
                existing.timestamp = timestamp
                existing.player_reports = 1
