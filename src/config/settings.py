"""Configuration management for HGE Notifier."""

import os
from pathlib import Path
from typing import Optional


class Settings:
    """Application settings loaded from environment variables and .env file."""

    def __init__(self) -> None:
        """Initialize settings from environment."""
        # Paths
        self.project_root: Path = Path(__file__).parent.parent.parent
        self.journal_path: Optional[Path] = self._parse_path(
            os.getenv("JOURNAL_PATH")
        )

        # EDDN Settings
        self.eddn_enabled: bool = self._parse_bool(
            os.getenv("EDDN_ENABLED", "true")
        )
        self.eddn_mock_mode: bool = self._parse_bool(
            os.getenv("EDDN_MOCK_MODE", "true")
        )

        # Refresh Settings
        self.refresh_interval: int = int(
            os.getenv("REFRESH_INTERVAL", "10")
        )

        # Web Settings
        self.web_host: str = os.getenv("WEB_HOST", "127.0.0.1")
        self.web_port: int = int(os.getenv("WEB_PORT", "5000"))
        self.web_debug: bool = self._parse_bool(
            os.getenv("WEB_DEBUG", "false")
        )

        # Logging
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.log_file: Optional[Path] = self._parse_path(
            os.getenv("LOG_FILE")
        )

    @staticmethod
    def _parse_bool(value: str) -> bool:
        """Parse string to boolean."""
        return value.lower() in ("true", "1", "yes", "on")

    @staticmethod
    def _parse_path(value: Optional[str]) -> Optional[Path]:
        """Parse string to Path object."""
        if value:
            return Path(value)
        return None

    def get_log_file_path(self) -> Optional[Path]:
        """Get the log file path, creating parent directories if needed."""
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            return self.log_file
        return None


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance (singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
