#!/usr/bin/env python3
"""Debug script to test coordinate fetching."""

import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from src.distance.coordinates import CoordinateDatabase

def main():
    """Test coordinate database."""
    db_path = Path(__file__).parent / "data"
    coord_db = CoordinateDatabase(db_path=db_path)
    
    # Test systems
    systems = ["Kruger 60", "Sol", "Shinrarta Dezhra"]
    
    for system_name in systems:
        print(f"\n{'='*60}")
        print(f"Testing: {system_name}")
        print('='*60)
        
        coords = coord_db.get_coordinates(system_name, use_cache=False)
        
        if coords:
            print(f"✓ Found coordinates: x={coords[0]}, y={coords[1]}, z={coords[2]}")
        else:
            print(f"✗ Failed to fetch coordinates")
    
    # Check cache stats
    print(f"\n{'='*60}")
    print("Cache Statistics")
    print('='*60)
    stats = coord_db.get_cache_stats()
    print(f"Total cached: {stats['total_cached']}")
    print(f"Recent cached: {stats['recent_cached']}")

if __name__ == "__main__":
    main()
