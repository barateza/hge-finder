"""Pytest configuration."""

import sys
from pathlib import Path
import pytest
from unittest.mock import patch

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(autouse=True)
def mock_system_info_lookup(request):
    """
    Mock SystemInfoLookup to avoid HTTP requests during tests.
    
    This fixture is automatically applied to all tests and prevents
    synchronous HTTP requests to EDSM API, which was causing tests
    to take 48+ seconds to complete (3-4 seconds per test with 
    signal enrichment).
    
    Exception: Tests in test_system_info.py are excluded so they can
    test SystemInfoLookup directly without global mocking.
    
    See: TEST_SLOWNESS_DIAGNOSIS.md for details.
    """
    # Skip mocking for system_info tests which need to test it directly
    test_module = request.module.__name__ if hasattr(request, 'module') else ""
    if "test_system_info" in test_module:
        # Let system_info tests manage their own mocking
        yield
        return
    
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
def mock_coordinate_database(request):
    """
    Mock CoordinateDatabase to avoid HTTP requests to EDSM API during tests.
    
    The CoordinateDatabase.get_coordinates() method makes HTTP requests to
    EDSM API with a 5-second timeout. This was causing remaining slowness.
    
    Returns mock coordinates: (10.0, 20.0, 30.0) for any system.
    
    Note: Tests that explicitly need to test error conditions (like those in
    test_coordinates.py with TestCoordinatesErrorHandling) are excluded from
    this mock so they can patch requests.get directly.
    
    See: TEST_SLOWNESS_DIAGNOSIS.md for details.
    """
    # Skip mocking for tests that explicitly test error conditions
    test_class = request.cls.__name__ if request.cls else ""
    if test_class == "TestCoordinatesErrorHandling":
        # Let these tests manage their own mocking
        yield
        return
    
    with patch('src.distance.coordinates.CoordinateDatabase.get_coordinates') as mock:
        # Return mock coordinates for any system
        mock.return_value = (10.0, 20.0, 30.0)
        yield mock
