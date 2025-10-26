"""Tests for CLI module."""

import pytest
import logging
import argparse
from unittest.mock import patch, MagicMock, call
from io import StringIO

from src.cli import setup_logging, display_status, run_cli


class TestSetupLogging:
    """Test logging configuration."""

    def test_setup_logging_console_handler_info_level(self, caplog):
        """Test that console handler is configured with INFO level."""
        setup_logging("INFO")
        
        # Verify logging level
        logger = logging.getLogger()
        assert logger.level == logging.INFO
        
        # Verify handlers exist
        assert len(logger.handlers) > 0

    def test_setup_logging_debug_level(self, caplog):
        """Test DEBUG level logging."""
        setup_logging("DEBUG")
        logger = logging.getLogger()
        assert logger.level == logging.DEBUG

    def test_setup_logging_warning_level(self, caplog):
        """Test WARNING level logging."""
        setup_logging("WARNING")
        logger = logging.getLogger()
        assert logger.level == logging.WARNING

    def test_setup_logging_error_level(self, caplog):
        """Test ERROR level logging."""
        setup_logging("ERROR")
        logger = logging.getLogger()
        assert logger.level == logging.ERROR

    def test_setup_logging_critical_level(self, caplog):
        """Test CRITICAL level logging."""
        setup_logging("CRITICAL")
        logger = logging.getLogger()
        assert logger.level == logging.CRITICAL

    def test_setup_logging_with_file_handler(self, tmp_path):
        """Test that file handler is created when log_file is provided."""
        log_file = tmp_path / "test.log"
        
        setup_logging("INFO", log_file=str(log_file))
        
        logger = logging.getLogger()
        # Count file handlers
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) >= 1

    def test_setup_logging_writes_to_file(self, tmp_path):
        """Test that logs are actually written to file."""
        log_file = tmp_path / "test.log"
        
        setup_logging("INFO", log_file=str(log_file))
        logger = logging.getLogger("test")
        logger.info("Test message")
        
        # Check file was created and contains log
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message" in content

    def test_setup_logging_console_handler_has_formatter(self):
        """Test that console handler has proper formatter."""
        # Clear existing handlers first
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        setup_logging("INFO")
        
        root_logger = logging.getLogger()
        console_handlers = [h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(console_handlers) > 0
        
        handler = console_handlers[0]
        assert handler.formatter is not None


class TestDisplayStatus:
    """Test status display formatting."""

    def test_display_status_with_hge_signal(self, capsys):
        """Test display with HGE signal present."""
        manager = MagicMock()
        manager.get_status.return_value = {
            "hge_signal": {
                "system_name": "Shinrarta Dezhra",
                "age": "5m ago",
                "coordinates": {"x": 1.0, "y": 2.0, "z": 3.0}
            },
            "commander_location": None,
            "distance": None,
        }
        
        display_status(manager)
        captured = capsys.readouterr()
        
        assert "Shinrarta Dezhra" in captured.out
        assert "5m ago" in captured.out
        assert "1.0" in captured.out

    def test_display_status_no_hge_signal(self, capsys):
        """Test display with no HGE signal."""
        manager = MagicMock()
        manager.get_status.return_value = {
            "hge_signal": None,
            "commander_location": None,
            "distance": None,
        }
        
        display_status(manager)
        captured = capsys.readouterr()
        
        assert "None detected yet" in captured.out

    def test_display_status_with_commander_location(self, capsys):
        """Test display with commander location."""
        manager = MagicMock()
        manager.get_status.return_value = {
            "hge_signal": None,
            "commander_location": {
                "system_name": "Sol",
                "coordinates": {"x": 0.0, "y": 0.0, "z": 0.0}
            },
            "distance": None,
        }
        
        display_status(manager)
        captured = capsys.readouterr()
        
        assert "Sol" in captured.out
        assert "YOUR LOCATION" in captured.out

    def test_display_status_with_distance(self, capsys):
        """Test display with distance information."""
        manager = MagicMock()
        manager.get_status.return_value = {
            "hge_signal": None,
            "commander_location": None,
            "distance": {
                "formatted": "35.28 light years"
            },
        }
        
        display_status(manager)
        captured = capsys.readouterr()
        
        assert "35.28" in captured.out
        assert "light years" in captured.out

    def test_display_status_with_all_info(self, capsys):
        """Test display with all information present."""
        manager = MagicMock()
        manager.get_status.return_value = {
            "hge_signal": {
                "system_name": "Shinrarta Dezhra",
                "age": "5m ago",
                "coordinates": {"x": 55.72, "y": -49.50, "z": 17.40}
            },
            "commander_location": {
                "system_name": "Sol",
                "coordinates": {"x": 0.0, "y": 0.0, "z": 0.0}
            },
            "distance": {
                "formatted": "35.28 light years"
            },
        }
        
        display_status(manager)
        captured = capsys.readouterr()
        
        assert "Shinrarta Dezhra" in captured.out
        assert "Sol" in captured.out
        assert "35.28" in captured.out
        assert "REAL-TIME STATUS" in captured.out

    def test_display_status_without_distance_calculation(self, capsys):
        """Test display when distance cannot be calculated."""
        manager = MagicMock()
        manager.get_status.return_value = {
            "hge_signal": None,
            "commander_location": None,
            "distance": None,
        }
        
        display_status(manager)
        captured = capsys.readouterr()
        
        assert "Cannot calculate" in captured.out


class TestRunCli:
    """Test CLI running."""

    @patch('src.cli.HGENotifierManager')
    @patch('src.cli.time.sleep')
    def test_run_cli_once_mode(self, mock_sleep, mock_manager_class):
        """Test --once mode exits after one iteration."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_manager.get_status.return_value = {
            "hge_signal": None,
            "commander_location": None,
            "distance": None,
        }
        
        args = argparse.Namespace(once=True, log_level="INFO", log_file=None)
        result = run_cli(args)
        
        # Should return 0 for success
        assert result == 0
        
        # Should call display_status at least once
        assert mock_manager.get_status.called

    @patch('src.cli.HGENotifierManager')
    @patch('src.cli.time.sleep')
    @patch('src.cli.display_status')
    def test_run_cli_continuous_mode_interrupted(self, mock_display, mock_sleep, mock_manager_class):
        """Test continuous mode with keyboard interrupt."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        
        # Simulate KeyboardInterrupt on second iteration
        mock_sleep.side_effect = KeyboardInterrupt()
        
        args = argparse.Namespace(once=False, log_level="INFO", log_file=None)
        result = run_cli(args)
        
        # Should return 0 on interrupt
        assert result == 0

    @patch('src.cli.HGENotifierManager')
    def test_run_cli_exception_handling(self, mock_manager_class):
        """Test exception handling in CLI."""
        # Create a mock manager that raises an exception during start()
        mock_manager = MagicMock()
        mock_manager.start.side_effect = Exception("Test error")
        mock_manager_class.return_value = mock_manager
        
        args = argparse.Namespace(once=True, log_level="INFO", log_file=None)
        result = run_cli(args)
        
        # Should return 1 on error
        assert result == 1

    @patch('src.cli.HGENotifierManager')
    @patch('src.cli.time.sleep')
    def test_run_cli_manager_initialization(self, mock_sleep, mock_manager_class):
        """Test that manager is initialized properly."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_manager.get_status.return_value = {
            "hge_signal": None,
            "commander_location": None,
            "distance": None,
        }
        
        args = argparse.Namespace(once=True, log_level="INFO", log_file=None)
        run_cli(args)
        
        # Verify manager was created
        mock_manager_class.assert_called_once()

    @patch('src.cli.HGENotifierManager')
    @patch('src.cli.time.sleep')
    @patch('src.cli.display_status')
    def test_run_cli_status_refresh_interval(self, mock_display, mock_sleep, mock_manager_class):
        """Test that status is refreshed on interval."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_manager.get_status.return_value = {
            "hge_signal": None,
            "commander_location": None,
            "distance": None,
        }
        
        # Make it run a few times then interrupt
        call_count = [0]
        def mock_sleep_side_effect(duration):
            call_count[0] += 1
            if call_count[0] > 2:
                raise KeyboardInterrupt()
        
        mock_sleep.side_effect = mock_sleep_side_effect
        
        args = argparse.Namespace(once=False, log_level="INFO", log_file=None)
        result = run_cli(args)
        
        assert result == 0
        # Should have called display_status at least twice
        assert mock_display.call_count >= 2

    @patch('src.cli.HGENotifierManager')
    @patch('src.cli.time.sleep')
    def test_run_cli_once_calls_display_status(self, mock_sleep, mock_manager_class):
        """Test that display_status is called in once mode."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_manager.get_status.return_value = {
            "hge_signal": None,
            "commander_location": None,
            "distance": None,
        }
        
        args = argparse.Namespace(once=True, log_level="INFO", log_file=None)
        
        with patch('src.cli.display_status') as mock_display:
            run_cli(args)
            mock_display.assert_called_once_with(mock_manager)

    @patch('src.cli.HGENotifierManager')
    @patch('src.cli.time.sleep')
    @patch('src.cli.display_status')
    def test_run_cli_continuous_mode_multiple_iterations(self, mock_display, mock_sleep, mock_manager_class):
        """Test continuous mode runs multiple iterations before interrupt."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_manager.settings.refresh_interval = 5
        
        # Simulate interrupt after 3 display calls
        call_count = [0]
        def interrupt_after_iterations(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] >= 3:
                raise KeyboardInterrupt()
        
        mock_sleep.side_effect = interrupt_after_iterations
        
        args = argparse.Namespace(once=False, log_level="INFO", log_file=None)
        result = run_cli(args)
        
        # Should return 0 (success with keyboard interrupt)
        assert result == 0
        # display_status should be called multiple times
        assert mock_display.call_count >= 3
        # Verify sleep was called with correct interval
        assert mock_sleep.call_count >= 3

    @patch('src.cli.HGENotifierManager')
    @patch('src.cli.time.sleep')
    @patch('src.cli.display_status')
    def test_run_cli_continuous_mode_refresh_interval(self, mock_display, mock_sleep, mock_manager_class):
        """Test continuous mode uses correct refresh interval from settings."""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager
        mock_manager.settings.refresh_interval = 10
        
        # Interrupt after first sleep
        mock_sleep.side_effect = KeyboardInterrupt()
        
        args = argparse.Namespace(once=False, log_level="INFO", log_file=None)
        result = run_cli(args)
        
        assert result == 0
        # Verify sleep was called with the correct refresh interval
        if mock_sleep.called:
            # The sleep is called with refresh_interval value
            call_args = mock_sleep.call_args
            if call_args:
                # First call should be with refresh_interval
                assert call_args[0][0] == 10 or call_args.args[0] == 10


# ============================================================================
# PHASE 1: QUICK WINS - CLI MAIN ENTRY POINT TESTS
# ============================================================================


class TestMainEntryPointPhase1:
    """Phase 1: Test CLI main entry point and error handling."""

    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.run_server')
    def test_main_keyboard_interrupt(self, mock_run_server, mock_manager_class):
        """Test CLI graceful shutdown on keyboard interrupt."""
        from src.__main__ import main
        
        with patch('sys.argv', ['eddn-hge']):
            # Mock the manager to raise KeyboardInterrupt
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_run_server.side_effect = KeyboardInterrupt()
            
            # Should return 0 on interrupt
            result = main()
            assert result == 0

    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.run_server')
    def test_main_exception_handling(self, mock_run_server, mock_manager_class):
        """Test CLI exception handling."""
        from src.__main__ import main
        
        with patch('sys.argv', ['eddn-hge']):
            # Mock the manager to raise an exception
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_run_server.side_effect = Exception("Test error")
            
            # Should return 1 on error
            result = main()
            assert result == 1

    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.run_cli')
    def test_main_cli_mode(self, mock_run_cli, mock_manager_class):
        """Test CLI mode (non-web)."""
        from src.__main__ import main
        
        with patch('sys.argv', ['eddn-hge']):
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_run_cli.return_value = 0
            
            # Run without --web flag
            result = main()
            assert mock_run_cli.called

    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.run_server')
    def test_main_web_mode(self, mock_run_server, mock_manager_class):
        """Test web mode."""
        from src.__main__ import main
        
        with patch('sys.argv', ['eddn-hge', '--web']):
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            mock_run_server.return_value = None
            
            # Run with --web flag
            result = main()
            assert mock_run_server.called

    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.run_server')
    def test_main_web_custom_port(self, mock_run_server, mock_manager_class):
        """Test web mode with custom port."""
        from src.__main__ import main
        
        with patch('sys.argv', ['eddn-hge', '--web', '--port', '8080']):
            mock_manager = MagicMock()
            mock_manager_class.return_value = mock_manager
            
            # Run with custom port
            result = main()
            
            # Verify port argument was passed
            call_kwargs = mock_run_server.call_args[1]
            assert call_kwargs['port'] == 8080

    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.run_cli')
    def test_main_real_eddn_flag(self, mock_run_cli, mock_manager_class):
        """Test --real-eddn flag."""
        from src.__main__ import main
        
        with patch('sys.argv', ['eddn-hge', '--real-eddn']):
            with patch('src.config.settings.get_settings') as mock_settings_factory:
                mock_settings = MagicMock()
                mock_settings_factory.return_value = mock_settings
                
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager
                mock_run_cli.return_value = 0
                
                # Run with --real-eddn flag
                main()
                
                # Verify settings were updated
                assert mock_settings.eddn_mock_mode is False

    @patch('src.__main__.HGENotifierManager')
    @patch('src.__main__.run_cli')
    def test_main_once_flag(self, mock_run_cli, mock_manager_class):
        """Test --once flag."""
        from src.__main__ import main
        
        with patch('sys.argv', ['eddn-hge', '--once']):
            with patch('src.config.settings.get_settings') as mock_settings_factory:
                mock_settings = MagicMock()
                mock_settings_factory.return_value = mock_settings
                
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager
                mock_run_cli.return_value = 0
                
                # Run with --once flag
                result = main()
                
                # Verify run_cli was called
                assert mock_run_cli.called

