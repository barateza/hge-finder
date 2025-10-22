"""Data models for the notification system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Tuple


@dataclass
class Alert:
    """Configuration for alert thresholds."""

    max_distance_ly: float = 50.0
    """Maximum distance in light years to send alert."""

    max_age_hours: int = 24
    """Maximum signal age in hours to send alert."""

    enabled: bool = True
    """Whether alerts are enabled."""

    def __post_init__(self):
        """Validate alert configuration."""
        if self.max_distance_ly < 0:
            raise ValueError("max_distance_ly must be positive")
        if self.max_age_hours < 0:
            raise ValueError("max_age_hours must be positive")


@dataclass
class Notification:
    """Represents a sent notification."""

    signal_system: str
    """Name of the system with HGE signal."""

    distance_ly: float
    """Distance to the HGE system in light years."""

    timestamp: datetime
    """When the notification was sent."""

    channel: str
    """Notification channel: 'discord' or 'in_app'."""

    success: bool
    """Whether notification was sent successfully."""

    error: Optional[str] = None
    """Error message if notification failed."""

    def __post_init__(self):
        """Validate notification."""
        if self.channel not in ("discord", "in_app"):
            raise ValueError("channel must be 'discord' or 'in_app'")
        if self.distance_ly < 0:
            raise ValueError("distance_ly must be positive")
