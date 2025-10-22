"""Notification manager - orchestrates all notification channels."""

import logging
import time
from typing import Optional
from datetime import datetime

from src.eddn import HGESignal
from src.journal import CommanderLocation
from src.distance import DistanceCalculator

from .models import Alert, Notification
from .in_app import InAppNotificationSystem
from .discord import DiscordNotificationService


logger = logging.getLogger(__name__)


class NotificationManager:
    """Orchestrate notification delivery across channels."""

    def __init__(
        self,
        discord_webhook: Optional[str] = None,
        alert_config: Optional[Alert] = None,
        cooldown_seconds: int = 60,
    ) -> None:
        """
        Initialize notification manager.

        Args:
            discord_webhook: Discord webhook URL or None to disable.
            alert_config: Alert threshold configuration.
            cooldown_seconds: Minimum seconds between notifications.
        """
        self.discord_service: Optional[DiscordNotificationService] = None
        if discord_webhook:
            try:
                self.discord_service = DiscordNotificationService(discord_webhook)
                logger.info("✅ Discord notification service initialized")
            except ValueError as e:
                logger.error(f"❌ Invalid Discord webhook: {e}")

        self.in_app = InAppNotificationSystem()
        self.alerts = alert_config or Alert()
        self.cooldown_seconds = cooldown_seconds
        self.last_notification_time: Optional[datetime] = None
        self.distance_calc = DistanceCalculator()

    def check_and_notify(
        self,
        signal: HGESignal,
        location: CommanderLocation,
    ) -> Optional[Notification]:
        """
        Check if signal meets alert criteria and send notifications.

        Args:
            signal: HGE signal to check.
            location: Commander's current location.

        Returns:
            Notification object if sent, None otherwise.
        """
        # Calculate distance
        distance = self.distance_calc.calculate_distance(
            signal.x, signal.y, signal.z,
            location.x, location.y, location.z,
        )

        if distance is None:
            logger.debug("Cannot calculate distance, skipping notification")
            return None

        # Check if signal meets thresholds
        if not self._meets_threshold(signal, distance):
            return None

        # Check cooldown
        if not self._check_cooldown():
            logger.debug("Notification cooldown active, skipping")
            return None

        # Send notifications to all enabled channels
        return self._send_notifications(
            signal, distance, location
        )

    def _meets_threshold(self, signal: HGESignal, distance: float) -> bool:
        """
        Check if signal meets alert thresholds.

        Args:
            signal: HGE signal.
            distance: Distance in light years.

        Returns:
            True if signal meets thresholds.
        """
        if not self.alerts.enabled:
            logger.debug("Alerts disabled")
            return False

        if distance > self.alerts.max_distance_ly:
            logger.debug(
                f"Signal too far: {distance:.2f}ly > {self.alerts.max_distance_ly}ly"
            )
            return False

        age_hours = signal.age_seconds() / 3600
        if age_hours > self.alerts.max_age_hours:
            logger.debug(
                f"Signal too old: {age_hours:.1f}h > {self.alerts.max_age_hours}h"
            )
            return False

        logger.debug(f"Signal meets thresholds: {distance:.2f}ly, {age_hours:.1f}h old")
        return True

    def _check_cooldown(self) -> bool:
        """
        Check if enough time has passed since last notification.

        Returns:
            True if cooldown has elapsed.
        """
        if self.last_notification_time is None:
            return True

        elapsed = (datetime.utcnow() - self.last_notification_time).total_seconds()
        if elapsed < self.cooldown_seconds:
            return False

        return True

    def _send_notifications(
        self,
        signal: HGESignal,
        distance: float,
        location: CommanderLocation,
    ) -> Optional[Notification]:
        """
        Send to all enabled notification channels.

        Args:
            signal: HGE signal.
            distance: Distance in light years.
            location: Commander location.

        Returns:
            Last Notification object sent.
        """
        notification = None

        # Update cooldown timer
        self.last_notification_time = datetime.utcnow()

        # Send Discord notification
        if self.discord_service:
            try:
                notification = self.discord_service.send_alert(
                    system_name=signal.system_name,
                    distance_ly=distance,
                    coordinates=(signal.x, signal.y, signal.z),
                    signal_age_hours=signal.age_seconds() / 3600,
                )
                self.in_app.add_notification(notification)
            except Exception as e:
                logger.error(f"Error sending Discord notification: {e}")

        # Send in-app notification
        in_app_notification = Notification(
            signal_system=signal.system_name,
            distance_ly=distance,
            timestamp=datetime.utcnow(),
            channel="in_app",
            success=True,
        )
        self.in_app.add_notification(in_app_notification)
        notification = in_app_notification

        logger.info(
            f"📢 Notifications sent for {signal.system_name} "
            f"({distance:.2f}ly away)"
        )

        return notification

    def get_notification_history(self, count: int = 10) -> list:
        """Get recent notifications."""
        return self.in_app.get_recent(count)

    def get_stats(self) -> dict:
        """Get notification statistics."""
        return self.in_app.get_stats()

    def clear_history(self) -> None:
        """Clear notification history."""
        self.in_app.clear_history()
