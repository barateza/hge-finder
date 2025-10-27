"""Signal grouping and aggregation module.

This module provides functionality to aggregate HGE signals by system and
material type, similar to edgalaxy.net. Instead of displaying individual
signals, we group them to show material counts and player confirmations.
"""

from src.signals.models import MaterialReport, SystemSignalGroup

__all__ = ["MaterialReport", "SystemSignalGroup"]
