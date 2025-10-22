"""Command-line interface for HGE Notifier."""

import argparse
import logging
import sys
import time
from typing import Optional

from src.core import HGENotifierManager


def setup_logging(log_level: str, log_file: Optional[str] = None) -> None:
    """Set up logging configuration."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        root_logger.addHandler(file_handler)


def display_status(manager: HGENotifierManager) -> None:
    """Display the current status in a formatted way."""
    status = manager.get_status()

    print("\n" + "=" * 70)
    print("HGE NOTIFIER - REAL-TIME STATUS")
    print("=" * 70)

    # HGE Signal
    if status["hge_signal"]:
        signal = status["hge_signal"]
        print(f"\n🔴 LATEST HGE SIGNAL")
        print(f"   System: {signal['system_name']}")
        print(f"   Age: {signal['age']}")
        print(f"   Coordinates: ({signal['coordinates']['x']}, "
              f"{signal['coordinates']['y']}, {signal['coordinates']['z']})")
    else:
        print("\n🔴 LATEST HGE SIGNAL: None detected yet")

    # Commander Location
    if status["commander_location"]:
        location = status["commander_location"]
        print(f"\n📍 YOUR LOCATION")
        print(f"   System: {location['system_name']}")
        print(f"   Coordinates: ({location['coordinates']['x']}, "
              f"{location['coordinates']['y']}, {location['coordinates']['z']})")
    else:
        print("\n📍 YOUR LOCATION: Unknown")

    # Distance
    if status["distance"]:
        distance_info = status["distance"]
        print(f"\n📏 DISTANCE TO HGE")
        print(f"   {distance_info['formatted']}")
    else:
        print("\n📏 DISTANCE TO HGE: Cannot calculate (missing data)")

    print("\n" + "=" * 70)


def run_cli(args: argparse.Namespace) -> int:
    """Run the CLI interface."""
    manager = HGENotifierManager()
    
    try:
        manager.start()
        
        if args.once:
            # Single run mode
            display_status(manager)
        else:
            # Continuous monitoring mode
            print("HGE Notifier running (press Ctrl+C to stop)...")
            print(f"Refresh interval: {manager.settings.refresh_interval} seconds")
            
            while True:
                display_status(manager)
                time.sleep(manager.settings.refresh_interval)
    
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        manager.stop()
    
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="HGE Notifier - Monitor Elite Dangerous EDDN for High Grade Emissions"
    )
    
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (don't continuously monitor)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    parser.add_argument(
        "--log-file",
        help="Log file path"
    )
    
    args = parser.parse_args()
    
    setup_logging(args.log_level, args.log_file)
    
    return run_cli(args)


if __name__ == "__main__":
    sys.exit(main())
