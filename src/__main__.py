"""Main entry point for HGE Notifier application."""

import argparse
import logging
import sys

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
  %(prog)s                    Run CLI with continuous monitoring
  %(prog)s --once             Run CLI once and exit
  %(prog)s --web              Run web server
  %(prog)s --web --port 8080  Run web server on custom port
        """,
    )
    
    parser.add_argument(
        "--web",
        action="store_true",
        help="Run web server instead of CLI"
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
