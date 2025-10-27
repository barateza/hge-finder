"""Command-line interface for HGE Notifier."""

import argparse
import logging
import os
import sys
import time
from typing import List, Optional

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


def get_status_indicator(age_seconds: Optional[float]) -> str:
    """
    Get colored status indicator based on signal age.
    
    Args:
        age_seconds: Age of the signal in seconds (or None if unknown).
    
    Returns:
        Status emoji/indicator string.
    """
    if age_seconds is None:
        return "⚪"  # Unknown
    elif age_seconds < 300:  # Less than 5 minutes
        return "🟢"  # Fresh
    elif age_seconds < 1800:  # Less than 30 minutes
        return "🟡"  # Recent
    elif age_seconds < 3600:  # Less than 1 hour
        return "🟠"  # Old
    else:
        return "🔴"  # Stale


def format_materials(materials: List[dict]) -> str:
    """
    Format materials list as compact display.
    
    Args:
        materials: List of material dictionaries with 'name' and 'count' keys.
    
    Returns:
        Formatted materials string with 💎 emoji and counts.
    """
    if not materials:
        return "None"
    
    material_strs = [f"{m['name']} ({m['count']})" for m in materials[:3]]
    result = " 💎 ".join(material_strs)
    
    if len(materials) > 3:
        result += f" +{len(materials) - 3} more"
    
    return result


def format_age(age_seconds: Optional[float]) -> str:
    """
    Format signal age as human-readable string.
    
    Args:
        age_seconds: Age in seconds or None.
    
    Returns:
        Formatted age string (e.g., "2m ago", "1h ago").
    """
    if age_seconds is None:
        return "Unknown"
    
    if age_seconds < 60:
        return f"{int(age_seconds)}s ago"
    elif age_seconds < 3600:
        minutes = int(age_seconds / 60)
        return f"{minutes}m ago"
    elif age_seconds < 86400:
        hours = int(age_seconds / 3600)
        return f"{hours}h ago"
    else:
        days = int(age_seconds / 86400)
        return f"{days}d ago"


def display_systems_table(
    systems: List[dict],
    commander_location: Optional[dict] = None,
    show_details: bool = False,
) -> None:
    """
    Display systems in a formatted ASCII table.
    
    Args:
        systems: List of system dictionaries from get_status()['active_systems'].
        commander_location: Optional commander location dictionary for context.
        show_details: If True, show additional details (allegiance, government, etc.).
    """
    if not systems:
        print("\n" + "⚪ No active HGE systems detected yet")
        return
    
    print("\n" + "=" * 130)
    print("HGE NOTIFIER - ACTIVE SYSTEMS")
    print("=" * 130)
    
    # Header
    headers = [
        "Status",
        "System",
        "Allegiance",
        "Materials",
        "Last Signal",
        "Reports",
        "Distance (ly)",
    ]
    
    if show_details:
        headers.extend(["State", "Population"])
    
    # Calculate column widths
    col_widths = {
        "Status": 8,
        "System": 20,
        "Allegiance": 12,
        "Materials": 50,
        "Last Signal": 12,
        "Reports": 10,
        "Distance (ly)": 15,
        "State": 12,
        "Population": 12,
    }
    
    # Print header
    header_line = " | ".join(
        f"{h:<{col_widths[h]}}" for h in headers
    )
    print(header_line)
    print("-" * 130)
    
    # Print rows
    for system in systems:
        status = get_status_indicator(system.get("last_signal_age"))
        system_name = system.get("system_name", "Unknown")[:19]
        allegiance = system.get("allegiance", "Unknown")[:11]
        materials = format_materials(system.get("materials", []))[:49]
        last_signal = format_age(system.get("last_signal_age"))[:11]
        reports = str(system.get("total_reports", 0))[:9]
        distance = f"{system.get('distance_ly', 'N/A')}"[:14]
        
        row_data = [
            f"{status:<{col_widths['Status']}}",
            f"{system_name:<{col_widths['System']}}",
            f"{allegiance:<{col_widths['Allegiance']}}",
            f"{materials:<{col_widths['Materials']}}",
            f"{last_signal:<{col_widths['Last Signal']}}",
            f"{reports:<{col_widths['Reports']}}",
            f"{distance:<{col_widths['Distance (ly)']}}",
        ]
        
        if show_details:
            state = system.get("state", "Unknown")[:11]
            population = str(system.get("population", 0))[:11]
            row_data.extend([
                f"{state:<{col_widths['State']}}",
                f"{population:<{col_widths['Population']}}",
            ])
        
        print(" | ".join(row_data))
    
    print("=" * 130)
    
    # Commander location
    if commander_location:
        loc_name = commander_location.get("system_name", "Unknown")
        print(f"📍 Your Location: {loc_name}")
    
    print(f"📊 Displaying {len(systems)} active systems\n")


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
    
    # Determine which display mode to use (with defaults for backward compatibility)
    use_table = getattr(args, "table", False) or getattr(args, "sort", None) or getattr(args, "material", None)
    refresh_count = 0
    
    try:
        manager.start()
        
        if args.once:
            # Single run mode
            if use_table:
                status = manager.get_status()
                systems = status.get("active_systems", [])
                
                # Apply sorting if requested
                sort_by = getattr(args, "sort", "recent")
                if sort_by == "distance":
                    systems = sorted(systems, key=lambda s: s.get("distance_ly", float('inf')))
                elif sort_by == "reports":
                    systems = sorted(systems, key=lambda s: s.get("total_reports", 0), reverse=True)
                # Default sort is "recent" (already sorted by manager)
                
                # Apply material filter if requested
                material = getattr(args, "material", None)
                if material:
                    filtered_systems = []
                    for system in systems:
                        materials_list = system.get("materials", [])
                        if any(m["name"].lower() == material.lower() for m in materials_list):
                            filtered_systems.append(system)
                    systems = filtered_systems
                
                show_details = getattr(args, "details", False)
                display_systems_table(
                    systems,
                    status.get("commander_location"),
                    show_details=show_details,
                )
            else:
                display_status(manager)
        else:
            # Continuous monitoring mode
            print("HGE Notifier running (press Ctrl+C to stop)...")
            print(f"Refresh interval: {manager.settings.refresh_interval} seconds")
            
            while True:
                if use_table:
                    # Clear screen before redrawing (works on Windows and Unix)
                    os.system("cls" if os.name == "nt" else "clear")
                    
                    status = manager.get_status()
                    systems = status.get("active_systems", [])
                    
                    # Apply sorting if requested
                    sort_by = getattr(args, "sort", "recent")
                    if sort_by == "distance":
                        systems = sorted(systems, key=lambda s: s.get("distance_ly", float('inf')))
                    elif sort_by == "reports":
                        systems = sorted(systems, key=lambda s: s.get("total_reports", 0), reverse=True)
                    # Default sort is "recent" (already sorted by manager)
                    
                    # Apply material filter if requested
                    material = getattr(args, "material", None)
                    if material:
                        filtered_systems = []
                        for system in systems:
                            materials_list = system.get("materials", [])
                            if any(m["name"].lower() == material.lower() for m in materials_list):
                                filtered_systems.append(system)
                        systems = filtered_systems
                    
                    # Print header with update info
                    print(f"[Update #{refresh_count + 1}] Last refresh: {time.strftime('%H:%M:%S')}")
                    
                    show_details = getattr(args, "details", False)
                    display_systems_table(
                        systems,
                        status.get("commander_location"),
                        show_details=show_details,
                    )
                else:
                    display_status(manager)
                
                refresh_count += 1
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
        "--table",
        action="store_true",
        help="Display systems in table format (default: simple view)"
    )
    parser.add_argument(
        "--sort",
        choices=["recent", "reports", "distance"],
        default="recent",
        help="Sort systems by: recent (last signal), reports (count), or distance (ly)"
    )
    parser.add_argument(
        "--material",
        type=str,
        help="Filter systems by material name (e.g., 'Proto Heat Radiators')"
    )
    parser.add_argument(
        "--details",
        action="store_true",
        help="Show additional system details (state, population) in table"
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
