"""Main entry point for HGE Notifier application."""

import argparse
import logging
import sys
import warnings

# Suppress the harmless runpy warning about __main__ module
warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*__main__.*")

from src.cli import setup_logging, run_cli
from src.config.settings import get_settings
from src.core import HGENotifierManager
from src.web import run_server


def main() -> int:
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="HGE Notifier - Monitor Elite Dangerous EDDN for High Grade Emissions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        Run CLI with continuous monitoring (mock mode)
  %(prog)s --real-eddn            Run CLI with real EDDN data
  %(prog)s --once                 Run CLI once and exit
  %(prog)s --web                  Run web server (mock mode)
  %(prog)s --web --real-eddn      Run web server with real EDDN data
  %(prog)s --web --port 8080      Run web server on custom port
        """,
    )
    
    parser.add_argument(
        "--web",
        action="store_true",
        help="Run web server instead of CLI"
    )
    parser.add_argument(
        "--real-eddn",
        action="store_true",
        help="Connect to real EDDN (default: use mock data for testing)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (CLI mode only)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Web server host (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Web server port (default: 5000)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--log-file",
        help="Log file path (optional)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    logger.info("HGE Notifier starting...")
    
    try:
        if args.web:
            # Web server mode
            settings = get_settings()
            
            # Override mock mode if requested
            if args.real_eddn:
                settings.eddn_mock_mode = False
                logger.info("Using real EDDN data")
            else:
                logger.info("Using mock EDDN data (use --real-eddn for real data)")
            
            manager = HGENotifierManager()
            
            logger.info(f"Starting web server on {args.host}:{args.port}")
            run_server(
                manager,
                host=args.host,
                port=args.port,
                debug=settings.web_debug,
            )
        else:
            # CLI mode
            settings = get_settings()
            
            # Override mock mode if requested
            if args.real_eddn:
                settings.eddn_mock_mode = False
                logger.info("Using real EDDN data")
            else:
                logger.info("Using mock EDDN data (use --real-eddn for real data)")
            
            parser_args = argparse.Namespace(
                once=args.once,
                log_level=args.log_level,
                log_file=args.log_file,
            )
            return run_cli(parser_args)
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 0
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
