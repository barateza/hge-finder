"""Tests for configuration module."""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.config.settings import Settings, get_settings


class TestSettingsConfiguration:
    """Test settings configuration and environment variable handling."""

    def test_settings_default_values(self):
        """Test that settings use default values when env vars are not set."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            # Check defaults
            assert settings.journal_path is None
            assert settings.eddn_enabled is True
            assert settings.eddn_mock_mode is True
            assert settings.refresh_interval == 10
            assert settings.web_host == "127.0.0.1"
            assert settings.web_port == 5000
            assert settings.web_debug is False
            assert settings.log_level == "INFO"

    def test_settings_refresh_interval_env_var(self):
        """Test REFRESH_INTERVAL environment variable is used."""
        with patch.dict(os.environ, {"REFRESH_INTERVAL": "30"}):
            settings = Settings()
            assert settings.refresh_interval == 30

    def test_settings_invalid_refresh_interval_defaults(self):
        """Test invalid REFRESH_INTERVAL falls back to default gracefully."""
        with patch.dict(os.environ, {"REFRESH_INTERVAL": "not_a_number"}):
            # Should raise ValueError during int() conversion
            with pytest.raises(ValueError):
                Settings()

    def test_settings_web_port_env_var(self):
        """Test WEB_PORT environment variable is used."""
        with patch.dict(os.environ, {"WEB_PORT": "8080"}):
            settings = Settings()
            assert settings.web_port == 8080

    def test_settings_web_host_env_var(self):
        """Test WEB_HOST environment variable is used."""
        with patch.dict(os.environ, {"WEB_HOST": "0.0.0.0"}):
            settings = Settings()
            assert settings.web_host == "0.0.0.0"

    def test_settings_log_level_env_var(self):
        """Test LOG_LEVEL environment variable is used."""
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            settings = Settings()
            assert settings.log_level == "DEBUG"

    def test_settings_journal_path_env_var(self):
        """Test JOURNAL_PATH environment variable is parsed to Path."""
        with patch.dict(os.environ, {"JOURNAL_PATH": "/path/to/journal"}):
            settings = Settings()
            assert settings.journal_path == Path("/path/to/journal")

    def test_settings_notifications_enabled_true(self):
        """Test NOTIFICATIONS_ENABLED env var set to true."""
        with patch.dict(os.environ, {"NOTIFICATIONS_ENABLED": "true"}):
            settings = Settings()
            assert settings.notifications_enabled is True

    def test_settings_notifications_enabled_false(self):
        """Test NOTIFICATIONS_ENABLED env var set to false."""
        with patch.dict(os.environ, {"NOTIFICATIONS_ENABLED": "false"}):
            settings = Settings()
            assert settings.notifications_enabled is False

    def test_settings_discord_webhook_url_env_var(self):
        """Test DISCORD_WEBHOOK_URL environment variable is used."""
        test_url = "https://discordapp.com/api/webhooks/test/token"
        with patch.dict(os.environ, {"DISCORD_WEBHOOK_URL": test_url}):
            settings = Settings()
            assert settings.discord_webhook_url == test_url

    def test_settings_alert_max_distance_env_var(self):
        """Test ALERT_MAX_DISTANCE environment variable is used."""
        with patch.dict(os.environ, {"ALERT_MAX_DISTANCE": "100.5"}):
            settings = Settings()
            assert settings.alert_max_distance == 100.5

    def test_settings_alert_max_age_env_var(self):
        """Test ALERT_MAX_AGE environment variable is used."""
        with patch.dict(os.environ, {"ALERT_MAX_AGE": "48.0"}):
            settings = Settings()
            assert settings.alert_max_age == 48.0

    def test_settings_notification_cooldown_env_var(self):
        """Test NOTIFICATION_COOLDOWN_SECONDS environment variable is used."""
        with patch.dict(os.environ, {"NOTIFICATION_COOLDOWN_SECONDS": "120"}):
            settings = Settings()
            assert settings.notification_cooldown_seconds == 120

    def test_settings_parse_bool_variations(self):
        """Test boolean parsing accepts multiple true/false values."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            # Test various true values
            assert settings._parse_bool("true") is True
            assert settings._parse_bool("True") is True
            assert settings._parse_bool("TRUE") is True
            assert settings._parse_bool("1") is True
            assert settings._parse_bool("yes") is True
            assert settings._parse_bool("YES") is True
            assert settings._parse_bool("on") is True
            assert settings._parse_bool("ON") is True
            
            # Test various false values
            assert settings._parse_bool("false") is False
            assert settings._parse_bool("False") is False
            assert settings._parse_bool("0") is False
            assert settings._parse_bool("no") is False
            assert settings._parse_bool("off") is False
            assert settings._parse_bool("anything_else") is False

    def test_settings_parse_path_valid(self):
        """Test path parsing with valid paths."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            path1 = settings._parse_path("/valid/path")
            assert path1 == Path("/valid/path")
            
            path2 = settings._parse_path("relative/path")
            assert path2 == Path("relative/path")

    def test_settings_parse_path_none(self):
        """Test path parsing with None/empty values."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            assert settings._parse_path(None) is None
            assert settings._parse_path("") is None

    def test_get_settings_singleton(self):
        """Test get_settings returns same instance (singleton pattern)."""
        # Reset the global settings first
        import src.config.settings as settings_module
        settings_module._settings = None
        
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Should be the same object
        assert settings1 is settings2

    def test_settings_get_log_file_path_creates_directories(self, tmp_path):
        """Test get_log_file_path creates parent directories if needed."""
        log_file = tmp_path / "logs" / "nested" / "test.log"
        
        with patch.dict(os.environ, {"LOG_FILE": str(log_file)}):
            settings = Settings()
            result_path = settings.get_log_file_path()
            
            # Parent directory should be created
            assert result_path.parent.exists()
            assert result_path == log_file

    def test_settings_get_log_file_path_none(self):
        """Test get_log_file_path returns None when log_file not set."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.get_log_file_path() is None

    def test_settings_multiple_env_vars_together(self):
        """Test multiple environment variables work together correctly."""
        env_vars = {
            "REFRESH_INTERVAL": "20",
            "WEB_HOST": "192.168.1.1",
            "WEB_PORT": "9000",
            "LOG_LEVEL": "WARNING",
            "NOTIFICATIONS_ENABLED": "true",
            "ALERT_MAX_DISTANCE": "75.0",
        }
        
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            
            assert settings.refresh_interval == 20
            assert settings.web_host == "192.168.1.1"
            assert settings.web_port == 9000
            assert settings.log_level == "WARNING"
            assert settings.notifications_enabled is True
            assert settings.alert_max_distance == 75.0

    def test_settings_web_debug_flag_variations(self):
        """Test WEB_DEBUG flag can be set to various true values."""
        for true_value in ["true", "1", "yes", "on"]:
            with patch.dict(os.environ, {"WEB_DEBUG": true_value}):
                settings = Settings()
                assert settings.web_debug is True, f"WEB_DEBUG={true_value} should be True"

    def test_settings_eddn_enabled_and_mock_mode(self):
        """Test EDDN_ENABLED and EDDN_MOCK_MODE can be controlled independently."""
        with patch.dict(os.environ, {"EDDN_ENABLED": "false", "EDDN_MOCK_MODE": "false"}):
            settings = Settings()
            assert settings.eddn_enabled is False
            assert settings.eddn_mock_mode is False

    def test_settings_project_root_path(self):
        """Test that project_root is set correctly."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            # Should point to repo root
            assert settings.project_root.exists()
            # Should contain pyproject.toml or other root files
            assert (settings.project_root / "pyproject.toml").exists() or \
                   (settings.project_root / "setup.py").exists() or \
                   (settings.project_root / ".git").exists()
