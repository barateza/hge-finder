"""
Phase 4: Systems Aggregation API Tests

Tests for new Phase 4 endpoints:
- GET /api/systems - Get all active systems
- GET /api/systems/<name> - Get specific system details
- GET /api/materials - Get all unique materials
- GET /api/materials/<name> - Get systems with specific material
- Material filtering and sorting
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from src.web import create_app
from src.core import HGENotifierManager
from src.eddn import HGESignal
from src.signals.models import SystemSignalGroup, MaterialReport


class TestSystemsAPIEndpoint:
    """Test GET /api/systems endpoint."""

    def test_systems_endpoint_returns_json(self):
        """Test /api/systems returns JSON response."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/systems")
            assert response.status_code == 200
            assert response.content_type == "application/json"

    def test_systems_endpoint_returns_success_status(self):
        """Test /api/systems returns success status."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/systems")
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "data" in data

    def test_systems_endpoint_returns_empty_list_initially(self):
        """Test /api/systems returns empty list when no systems."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/systems")
            data = json.loads(response.data)
            assert data["data"] == []
            assert data["count"] == 0

    def test_systems_endpoint_with_sort_by_parameter(self):
        """Test /api/systems accepts sort_by parameter."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            for sort_type in ["recent", "reports", "distance"]:
                response = client.get(f"/api/systems?sort_by={sort_type}")
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data["sort_by"] == sort_type

    def test_systems_endpoint_with_material_filter(self):
        """Test /api/systems accepts material filter parameter."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/systems?material=Imperial%20Shielding")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["material_filter"] == "Imperial Shielding"

    def test_systems_endpoint_with_limit_parameter(self):
        """Test /api/systems accepts limit parameter."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/systems?limit=10")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data["data"]) <= 10


class TestSystemDetailEndpoint:
    """Test GET /api/systems/<name> endpoint."""

    def test_system_detail_404_for_nonexistent_system(self):
        """Test /api/systems/<name> returns 404 for nonexistent system."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/systems/NonexistentSystem")
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data["status"] == "error"

    def test_system_detail_endpoint_returns_json(self):
        """Test /api/systems/<name> returns JSON."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/systems/TestSystem")
            assert response.content_type == "application/json"

    def test_system_detail_contains_required_fields(self):
        """Test /api/systems/<name> response contains required fields."""
        manager = HGENotifierManager()
        
        # Add a test signal
        signal = HGESignal(
            system_name="TestSystem",
            allegiance="Federation",
            state="Boom",
            x=100.0, y=200.0, z=300.0,
            timestamp=datetime.now(timezone.utc),
        )
        manager._on_new_hge_signal(signal)
        
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/systems/TestSystem")
            data = json.loads(response.data)
            
            assert response.status_code == 200
            assert data["status"] == "success"
            assert "material_breakdown" in data["data"]


class TestMaterialsEndpoint:
    """Test GET /api/materials endpoint."""

    def test_materials_endpoint_returns_json(self):
        """Test /api/materials returns JSON."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/materials")
            assert response.status_code == 200
            assert response.content_type == "application/json"

    def test_materials_endpoint_returns_success(self):
        """Test /api/materials returns success status."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/materials")
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "data" in data

    def test_materials_endpoint_returns_empty_list_initially(self):
        """Test /api/materials returns empty list initially."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/materials")
            data = json.loads(response.data)
            assert data["data"] == []
            assert data["count"] == 0

    def test_materials_data_structure(self):
        """Test /api/materials returns correct data structure."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/materials")
            data = json.loads(response.data)
            
            # Each material should have: name, occurrences, total_reports
            for material in data["data"]:
                assert "name" in material
                assert "occurrences" in material
                assert "total_reports" in material


class TestMaterialFilterEndpoint:
    """Test GET /api/materials/<material> endpoint."""

    def test_material_filter_returns_json(self):
        """Test /api/materials/<material> returns JSON."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/materials/Imperial%20Shielding")
            assert response.status_code == 200
            assert response.content_type == "application/json"

    def test_material_filter_returns_success(self):
        """Test /api/materials/<material> returns success."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/materials/Imperial%20Shielding")
            data = json.loads(response.data)
            assert data["status"] == "success"

    def test_material_filter_returns_empty_list_initially(self):
        """Test /api/materials/<material> returns empty list initially."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/materials/Imperial%20Shielding")
            data = json.loads(response.data)
            assert data["data"] == []
            assert data["count"] == 0

    def test_material_filter_accepts_limit_parameter(self):
        """Test /api/materials/<material> accepts limit parameter."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/materials/Imperial%20Shielding?limit=5")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data["data"]) <= 5


class TestSystemsAPIWithData:
    """Test systems API endpoints with actual data."""

    def test_systems_endpoint_with_multiple_systems(self):
        """Test /api/systems returns multiple systems."""
        manager = HGENotifierManager()
        
        # Add multiple test signals
        for i in range(3):
            signal = HGESignal(
                system_name=f"TestSystem{i}",
                allegiance="Federation",
                state="Boom",
                x=100.0 + i, y=200.0 + i, z=300.0 + i,
                timestamp=datetime.now(timezone.utc),
            )
            manager._on_new_hge_signal(signal)
        
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/systems")
            data = json.loads(response.data)
            assert len(data["data"]) == 3

    def test_systems_endpoint_sorts_by_distance_when_requested(self):
        """Test /api/systems can sort by distance when requested."""
        manager = HGENotifierManager()
        
        # Add multiple signals
        for i in range(3):
            signal = HGESignal(
                system_name=f"TestSystem{i}",
                allegiance="Federation",
                state="Boom",
                x=100.0 + (i * 10), y=200.0 + (i * 10), z=300.0 + (i * 10),
                timestamp=datetime.now(timezone.utc),
            )
            manager._on_new_hge_signal(signal)
        
        app = create_app(manager)

        with app.test_client() as client:
            # Test that distance sorting is accepted
            response = client.get("/api/systems?sort_by=distance")
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["sort_by"] == "distance"

    def test_system_detail_returns_material_breakdown(self):
        """Test /api/systems/<name> includes material breakdown."""
        manager = HGENotifierManager()
        
        # Add a signal
        signal = HGESignal(
            system_name="TestSystem",
            allegiance="Federation",
            state="Boom",
            x=100.0, y=200.0, z=300.0,
            timestamp=datetime.now(timezone.utc),
        )
        manager._on_new_hge_signal(signal)
        
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/systems/TestSystem")
            data = json.loads(response.data)
            
            assert response.status_code == 200
            assert "material_breakdown" in data["data"]
            assert isinstance(data["data"]["material_breakdown"], list)


class TestAPIErrorHandling:
    """Test error handling in new API endpoints."""

    def test_systems_api_handles_internal_errors_gracefully(self):
        """Test /api/systems handles internal errors."""
        manager = HGENotifierManager()
        
        with patch.object(manager.signal_merger, 'get_active_systems') as mock_method:
            mock_method.side_effect = Exception("Test error")
            app = create_app(manager)

            with app.test_client() as client:
                response = client.get("/api/systems")
                assert response.status_code == 500
                data = json.loads(response.data)
                assert data["status"] == "error"

    def test_materials_api_handles_internal_errors_gracefully(self):
        """Test /api/materials handles internal errors."""
        manager = HGENotifierManager()
        
        with patch.object(manager.signal_merger, 'get_all_materials') as mock_method:
            mock_method.side_effect = Exception("Test error")
            app = create_app(manager)

            with app.test_client() as client:
                response = client.get("/api/materials")
                assert response.status_code == 500
                data = json.loads(response.data)
                assert data["status"] == "error"

    def test_system_detail_api_handles_errors(self):
        """Test /api/systems/<name> handles errors."""
        manager = HGENotifierManager()
        
        with patch.object(manager.signal_merger, 'get_system_by_name') as mock_method:
            mock_method.side_effect = Exception("Test error")
            app = create_app(manager)

            with app.test_client() as client:
                response = client.get("/api/systems/TestSystem")
                assert response.status_code == 500


class TestAPIResponseStructure:
    """Test response structure of new endpoints."""

    def test_systems_response_has_required_fields(self):
        """Test /api/systems response has all required fields."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/systems")
            data = json.loads(response.data)
            
            assert "status" in data
            assert "data" in data
            assert "count" in data
            assert "sort_by" in data
            assert "material_filter" in data

    def test_system_detail_response_structure(self):
        """Test /api/systems/<name> response structure."""
        manager = HGENotifierManager()
        
        # Add a test signal
        signal = HGESignal(
            system_name="TestSystem",
            allegiance="Federation",
            state="Boom",
            x=100.0, y=200.0, z=300.0,
            timestamp=datetime.now(timezone.utc),
        )
        manager._on_new_hge_signal(signal)
        
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/systems/TestSystem")
            data = json.loads(response.data)
            
            assert "status" in data
            assert "data" in data
            if response.status_code == 200:
                system_data = data["data"]
                assert "system_name" in system_data
                assert "materials" in system_data
                assert "material_breakdown" in system_data

    def test_materials_response_structure(self):
        """Test /api/materials response structure."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/materials")
            data = json.loads(response.data)
            
            assert "status" in data
            assert "data" in data
            assert "count" in data

    def test_material_filter_response_structure(self):
        """Test /api/materials/<material> response structure."""
        manager = HGENotifierManager()
        app = create_app(manager)

        with app.test_client() as client:
            response = client.get("/api/materials/Imperial%20Shielding")
            data = json.loads(response.data)
            
            assert "status" in data
            assert "data" in data
            assert "count" in data
            assert "material" in data
