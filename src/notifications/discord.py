"""Discord webhook integration for HGE notifications."""

import logging
import time
from typing import Optional, Tuple
from datetime import datetime

import requests

from .models import Notification


logger = logging.getLogger(__name__)


class DiscordNotificationService:
    """Send alerts to Discord via webhook."""

    MAX_RETRY_ATTEMPTS = 3
    INITIAL_RETRY_DELAY = 1  # seconds

    def __init__(self, webhook_url: str, timeout: int = 5) -> None:
        """
        Initialize Discord notification service.

        Args:
            webhook_url: Discord webhook URL.
            timeout: Request timeout in seconds.

        Raises:
            ValueError: If webhook URL is invalid.
        """
        if not webhook_url or not webhook_url.startswith("https://"):
            raise ValueError("Invalid Discord webhook URL")

        self.webhook_url = webhook_url
        self.timeout = timeout

    def send_alert(
        self,
        system_name: str,
        distance_ly: float,
        coordinates: Optional[Tuple[float, float, float]],
        signal_age_hours: float,
    ) -> Notification:
        """
        Send HGE alert to Discord.

        Args:
            system_name: Name of the system with HGE signal.
            distance_ly: Distance in light years.
            coordinates: (x, y, z) coordinates or None.
            signal_age_hours: Age of signal in hours.

        Returns:
            Notification object with delivery status.
        """
        embed = self._build_embed(
            system_name=system_name,
            distance_ly=distance_ly,
            coordinates=coordinates,
            signal_age_hours=signal_age_hours,
        )

        payload = {"embeds": [embed]}

        success, error = self._send_with_retry(payload)

        notification = Notification(
            signal_system=system_name,
            distance_ly=distance_ly,
            timestamp=datetime.utcnow(),
            channel="discord",
            success=success,
            error=error,
        )

        if success:
            logger.info(f"✅ Discord alert sent for {system_name}")
        else:
            logger.error(f"❌ Failed to send Discord alert: {error}")

        return notification

    def _build_embed(
        self,
        system_name: str,
        distance_ly: float,
        coordinates: Optional[Tuple[float, float, float]],
        signal_age_hours: float,
    ) -> dict:
        """
        Build Discord embed message.

        Args:
            system_name: System name.
            distance_ly: Distance in light years.
            coordinates: System coordinates or None.
            signal_age_hours: Signal age in hours.

        Returns:
            Dictionary representing Discord embed.
        """
        # Format coordinates
        if coordinates:
            coords_str = f"({coordinates[0]:.2f}, {coordinates[1]:.2f}, {coordinates[2]:.2f})"
        else:
            coords_str = "Unknown"

        # Format distance
        distance_str = f"{distance_ly:.2f} ly"

        # Format signal age
        if signal_age_hours < 1:
            age_str = f"{int(signal_age_hours * 60)}m ago"
        elif signal_age_hours < 24:
            age_str = f"{int(signal_age_hours)}h ago"
        else:
            age_str = f"{int(signal_age_hours / 24)}d ago"

        embed = {
            "title": "🎯 NEW HGE SIGNAL DETECTED",
            "description": f"High Grade Emission found in **{system_name}**",
            "color": 16711680,  # Red color
            "fields": [
                {
                    "name": "System",
                    "value": system_name,
                    "inline": False,
                },
                {
                    "name": "Distance",
                    "value": distance_str,
                    "inline": True,
                },
                {
                    "name": "Signal Age",
                    "value": age_str,
                    "inline": True,
                },
                {
                    "name": "Coordinates",
                    "value": coords_str,
                    "inline": False,
                },
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }

        return embed

    def _send_with_retry(self, payload: dict) -> Tuple[bool, Optional[str]]:
        """
        Send to Discord with exponential backoff retry logic.

        Args:
            payload: Discord webhook payload.

        Returns:
            Tuple of (success, error_message).
        """
        delay = self.INITIAL_RETRY_DELAY

        for attempt in range(self.MAX_RETRY_ATTEMPTS):
            try:
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    timeout=self.timeout,
                )

                if response.status_code in (200, 204):
                    return True, None

                if response.status_code == 429:
                    # Rate limited
                    logger.warning(f"Discord rate limited, retry {attempt + 1}/{self.MAX_RETRY_ATTEMPTS}")
                    time.sleep(delay)
                    delay *= 2
                    continue

                error = f"HTTP {response.status_code}"
                logger.error(f"Discord API error: {error}")
                return False, error

            except requests.Timeout:
                error = "Request timeout"
                logger.warning(f"Discord timeout (attempt {attempt + 1}/{self.MAX_RETRY_ATTEMPTS})")

                if attempt < self.MAX_RETRY_ATTEMPTS - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue

                return False, error

            except requests.ConnectionError as e:
                error = f"Connection error: {str(e)}"
                logger.warning(f"Discord connection error: {error}")

                if attempt < self.MAX_RETRY_ATTEMPTS - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue

                return False, error

            except Exception as e:
                error = f"Unexpected error: {str(e)}"
                logger.error(f"Discord notification error: {error}")
                return False, error

        return False, "Max retries exceeded"
