"""In-app notification storage and management."""

import logging
from typing import List, Optional
from datetime import datetime

from .models import Notification


logger = logging.getLogger(__name__)


class InAppNotificationSystem:
    """Store and manage in-app notifications."""

    def __init__(self, max_history: int = 100) -> None:
        """
        Initialize in-app notification system.

        Args:
            max_history: Maximum number of notifications to keep in memory.
        """
        self.history: List[Notification] = []
        self.max_history = max_history

    def add_notification(self, notification: Notification) -> None:
        """
        Add a notification to history.

        Args:
            notification: Notification object to add.
        """
        self.history.append(notification)

        # Trim history if exceeds max
        if len(self.history) > self.max_history:
            removed = self.history.pop(0)
            logger.debug(f"Removed old notification: {removed.signal_system}")

    def get_recent(self, count: int = 10) -> List[Notification]:
        """
        Get recent notifications.

        Args:
            count: Number of recent notifications to retrieve.

        Returns:
            List of Notification objects, most recent last.
        """
        return self.history[-count:] if self.history else []

    def get_all(self) -> List[Notification]:
        """Get all notifications in history."""
        return self.history.copy()

    def clear_history(self) -> None:
        """Clear all notification history."""
        count = len(self.history)
        self.history.clear()
        logger.info(f"Cleared {count} notifications from history")

    def get_stats(self) -> dict:
        """
        Get notification statistics.

        Returns:
            Dictionary with statistics about notifications.
        """
        discord_success = sum(
            1
            for n in self.history
            if n.channel == "discord" and n.success
        )
        discord_failed = sum(
            1
            for n in self.history
            if n.channel == "discord" and not n.success
        )
        in_app_count = sum(
            1
            for n in self.history
            if n.channel == "in_app"
        )

        return {
            "total": len(self.history),
            "discord_success": discord_success,
            "discord_failed": discord_failed,
            "in_app": in_app_count,
            "max_history": self.max_history,
        }

    def get_by_system(self, system_name: str) -> List[Notification]:
        """
        Get all notifications for a specific system.

        Args:
            system_name: Name of the system.

        Returns:
            List of Notification objects for that system.
        """
        return [n for n in self.history if n.signal_system == system_name]

    def get_failed_notifications(self) -> List[Notification]:
        """Get all failed notifications for debugging."""
        return [n for n in self.history if not n.success]
