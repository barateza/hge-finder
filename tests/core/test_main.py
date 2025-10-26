"""Tests for __main__ entry point."""

import pytest
import sys
import argparse
from unittest.mock import patch, MagicMock, call

from src.__main__ import main


class TestMainEntry:
    """Test main application entry point."""

    @patch('src.__main__.run_cli')
    @patch('src.__main__.setup_logging')
    def test_cli_mode_default(self, mock_setup_logging, mock_run_cli):
        """Test CLI mode (no --web flag) with default arguments."""
        mock_run_cli.return_value = 0
        
        sys.argv = ["hge_notifier"]
        result = main()
        
        # Should call run_cli
        mock_run_cli.assert_called_once()
        # Should return 0
        assert result == 0

    @patch('src.__main__.run_server')
    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.get_settings')
    @patch('src.__main__.setup_logging')
    def test_web_mode(self, mock_setup_logging, mock_get_settings, mock_manager_class, mock_run_server):
        """Test web server mode (--web flag)."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_settings = MagicMock()
        mock_settings.web_debug = False
        mock_get_settings.return_value = mock_settings
        
        sys.argv = ["hge_notifier", "--web"]
        result = main()
        
        # Should call run_server
        mock_run_server.assert_called_once()
        # Should return 0
        assert result == 0

    @patch('src.__main__.run_server')
    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.get_settings')
    @patch('src.__main__.setup_logging')
    def test_web_mode_with_custom_port(self, mock_setup_logging, mock_get_settings, mock_manager_class, mock_run_server):
        """Test web server mode with custom port."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_settings = MagicMock()
        mock_settings.web_debug = False
        mock_get_settings.return_value = mock_settings
        
        sys.argv = ["hge_notifier", "--web", "--port", "8080"]
        result = main()
        
        # Verify run_server was called with port 8080
        call_args = mock_run_server.call_args
        assert call_args[1]["port"] == 8080
        assert result == 0

    @patch('src.__main__.run_server')
    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.get_settings')
    @patch('src.__main__.setup_logging')
    def test_web_mode_with_custom_host(self, mock_setup_logging, mock_get_settings, mock_manager_class, mock_run_server):
        """Test web server mode with custom host."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_settings = MagicMock()
        mock_settings.web_debug = False
        mock_get_settings.return_value = mock_settings
        
        sys.argv = ["hge_notifier", "--web", "--host", "0.0.0.0"]
        result = main()
        
        # Verify run_server was called with host 0.0.0.0
        call_args = mock_run_server.call_args
        assert call_args[1]["host"] == "0.0.0.0"
        assert result == 0

    @patch('src.__main__.run_server')
    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.get_settings')
    @patch('src.__main__.setup_logging')
    def test_web_mode_with_host_and_port(self, mock_setup_logging, mock_get_settings, mock_manager_class, mock_run_server):
        """Test web server mode with both host and port."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_settings = MagicMock()
        mock_settings.web_debug = False
        mock_get_settings.return_value = mock_settings
        
        sys.argv = ["hge_notifier", "--web", "--host", "192.168.1.1", "--port", "9000"]
        result = main()
        
        call_args = mock_run_server.call_args
        assert call_args[1]["host"] == "192.168.1.1"
        assert call_args[1]["port"] == 9000
        assert result == 0

    @patch('src.__main__.run_cli')
    @patch('src.__main__.setup_logging')
    def test_keyboard_interrupt_in_cli(self, mock_setup_logging, mock_run_cli):
        """Test graceful handling of Ctrl+C in CLI mode."""
        mock_run_cli.side_effect = KeyboardInterrupt()
        
        sys.argv = ["hge_notifier"]
        result = main()
        
        # Should return 0 on interrupt
        assert result == 0

    @patch('src.__main__.run_cli')
    @patch('src.__main__.setup_logging')
    def test_exception_handling_in_cli(self, mock_setup_logging, mock_run_cli):
        """Test exception handling in CLI mode."""
        mock_run_cli.side_effect = Exception("Test error")
        
        sys.argv = ["hge_notifier"]
        result = main()
        
        # Should return 1 on error
        assert result == 1

    @patch('src.__main__.run_server')
    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.get_settings')
    @patch('src.__main__.setup_logging')
    def test_keyboard_interrupt_in_web(self, mock_setup_logging, mock_get_settings, mock_manager_class, mock_run_server):
        """Test graceful handling of Ctrl+C in web mode."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_settings = MagicMock()
        mock_settings.web_debug = False
        mock_get_settings.return_value = mock_settings
        mock_run_server.side_effect = KeyboardInterrupt()
        
        sys.argv = ["hge_notifier", "--web"]
        result = main()
        
        # Should return 0 on interrupt
        assert result == 0

    @patch('src.__main__.run_server')
    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.get_settings')
    @patch('src.__main__.setup_logging')
    def test_exception_handling_in_web(self, mock_setup_logging, mock_get_settings, mock_manager_class, mock_run_server):
        """Test exception handling in web mode."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_settings = MagicMock()
        mock_settings.web_debug = False
        mock_get_settings.return_value = mock_settings
        mock_run_server.side_effect = Exception("Server error")
        
        sys.argv = ["hge_notifier", "--web"]
        result = main()
        
        # Should return 1 on error
        assert result == 1

    @patch('src.__main__.run_cli')
    @patch('src.__main__.setup_logging')
    def test_log_level_debug(self, mock_setup_logging, mock_run_cli):
        """Test --log-level DEBUG option."""
        mock_run_cli.return_value = 0
        
        sys.argv = ["hge_notifier", "--log-level", "DEBUG"]
        result = main()
        
        # Verify setup_logging was called with DEBUG
        call_args = mock_setup_logging.call_args
        assert call_args[0][0] == "DEBUG"

    @patch('src.__main__.run_cli')
    @patch('src.__main__.setup_logging')
    def test_log_level_warning(self, mock_setup_logging, mock_run_cli):
        """Test --log-level WARNING option."""
        mock_run_cli.return_value = 0
        
        sys.argv = ["hge_notifier", "--log-level", "WARNING"]
        result = main()
        
        call_args = mock_setup_logging.call_args
        assert call_args[0][0] == "WARNING"

    @patch('src.__main__.run_cli')
    @patch('src.__main__.setup_logging')
    def test_log_file_option(self, mock_setup_logging, mock_run_cli):
        """Test --log-file option."""
        mock_run_cli.return_value = 0
        
        sys.argv = ["hge_notifier", "--log-file", "/tmp/test.log"]
        result = main()
        
        # Verify setup_logging was called with log file
        call_args = mock_setup_logging.call_args
        assert call_args[0][1] == "/tmp/test.log"

    @patch('src.__main__.run_cli')
    @patch('src.__main__.setup_logging')
    def test_once_flag(self, mock_setup_logging, mock_run_cli):
        """Test --once flag."""
        mock_run_cli.return_value = 0
        
        sys.argv = ["hge_notifier", "--once"]
        result = main()
        
        # Verify run_cli was called
        mock_run_cli.assert_called_once()
        
        # Verify the args passed include once=True
        call_args = mock_run_cli.call_args[0][0]
        assert call_args.once is True

    @patch('src.__main__.run_cli')
    @patch('src.__main__.setup_logging')
    def test_combined_options(self, mock_setup_logging, mock_run_cli):
        """Test combination of options."""
        mock_run_cli.return_value = 0
        
        sys.argv = ["hge_notifier", "--once", "--log-level", "DEBUG", "--log-file", "/tmp/test.log"]
        result = main()
        
        # Verify setup_logging was called correctly
        setup_call_args = mock_setup_logging.call_args
        assert setup_call_args[0][0] == "DEBUG"
        assert setup_call_args[0][1] == "/tmp/test.log"
        
        # Verify run_cli was called
        mock_run_cli.assert_called_once()

    @patch('src.__main__.run_server')
    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.get_settings')
    @patch('src.__main__.setup_logging')
    def test_web_debug_setting(self, mock_setup_logging, mock_get_settings, mock_manager_class, mock_run_server):
        """Test that web_debug setting is passed to run_server."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_settings = MagicMock()
        mock_settings.web_debug = True
        mock_get_settings.return_value = mock_settings
        
        sys.argv = ["hge_notifier", "--web"]
        result = main()
        
        # Verify debug=True was passed to run_server
        call_args = mock_run_server.call_args
        assert call_args[1]["debug"] is True

    @patch('src.__main__.run_cli')
    @patch('src.__main__.setup_logging')
    def test_default_log_level(self, mock_setup_logging, mock_run_cli):
        """Test that default log level is INFO."""
        mock_run_cli.return_value = 0
        
        sys.argv = ["hge_notifier"]
        result = main()
        
        # Verify setup_logging was called with INFO
        call_args = mock_setup_logging.call_args
        assert call_args[0][0] == "INFO"

    @patch('src.__main__.run_server')
    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.get_settings')
    @patch('src.__main__.setup_logging')
    def test_default_host_and_port(self, mock_setup_logging, mock_get_settings, mock_manager_class, mock_run_server):
        """Test that default host and port are used."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_settings = MagicMock()
        mock_settings.web_debug = False
        mock_get_settings.return_value = mock_settings
        
        sys.argv = ["hge_notifier", "--web"]
        result = main()
        
        # Verify default host and port
        call_args = mock_run_server.call_args
        assert call_args[1]["host"] == "127.0.0.1"
        assert call_args[1]["port"] == 5000
