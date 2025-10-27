"""Pytest configuration."""

import sys
from pathlib import Path
import pytest
from unittest.mock import patch

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def mock_system_info_lookup():
    """
    Mock SystemInfoLookup to avoid HTTP requests during tests.
    
    This fixture is automatically applied to all tests and prevents
    synchronous HTTP requests to EDSM API, which was causing tests
    to take 48+ seconds to complete (3-4 seconds per test with 
    signal enrichment).
    
    See: TEST_SLOWNESS_DIAGNOSIS.md for details.
    """
    mock_system_info = {
        'allegiance': 'Federation',
        'government': 'Democracy',
        'population': 1000000,
        'state': 'None',
    }
    
    with patch('src.system_info.SystemInfoLookup.get_system_info') as mock:
        mock.return_value = mock_system_info
        yield mock


@pytest.fixture(autouse=True)
def mock_coordinate_database():
    """
    Mock CoordinateDatabase to avoid HTTP requests to EDSM API during tests.
    
    The CoordinateDatabase.get_coordinates() method makes HTTP requests to
    EDSM API with a 5-second timeout. This was causing remaining slowness.
    
    Returns mock coordinates: (10.0, 20.0, 30.0) for any system.
    
    See: TEST_SLOWNESS_DIAGNOSIS.md for details.
    """
    with patch('src.distance.coordinates.CoordinateDatabase.get_coordinates') as mock:
        # Return mock coordinates for any system
        mock.return_value = (10.0, 20.0, 30.0)
        yield mock
