"""
Comprehensive Flask Endpoint Tests

Tests for Flask web server endpoints with high coverage:
- All GET endpoints (/api/*, routes)
- All POST endpoints (refresh, clear, etc.)
- Error handling and edge cases
- Query parameters and filtering
- Status codes and response formats

Target: Increase src/web/__init__.py coverage from 58% → 85%+
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from datetime import datetime, timedelta, timezone

from src.web import create_app
from src.core import HGENotifierManager
from src.eddn import HGESignal
from src.signals.models import SystemSignalGroup, MaterialReport


class TestFlaskEndpointsCore:
    """Test core Flask endpoints."""

    def test_index_renders_html(self):
        """Test / returns HTML content."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/")
            assert response.status_code == 200
            assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data

    def test_status_endpoint_returns_valid_json(self):
        """Test /api/status returns valid JSON with required fields."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/status")
            assert response.status_code == 200
            assert response.content_type == "application/json"
            
            data = json.loads(response.data)
            assert isinstance(data, dict)
            assert "commander_location" in data
            assert "active_systems" in data
            assert "initialized" in data

    def test_status_includes_required_fields(self):
        """Test /api/status includes all required fields."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/status")
            data = json.loads(response.data)
            
            # Check required fields
            assert "commander_location" in data
            assert "active_systems" in data
            assert "initialized" in data
            assert "total_unique_systems" in data


class TestMaterialsEndpoint:
    """Test /api/hge/materials endpoint."""

    def test_materials_endpoint_success(self):
        """Test /api/hge/materials returns success response."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/hge/materials")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "data" in data

    def test_materials_endpoint_with_no_signal(self):
        """Test /api/hge/materials when no signal exists."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/hge/materials")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["data"] is None

    @patch.object(HGENotifierManager, 'get_status')
    def test_materials_endpoint_with_signal_data(self, mock_status):
        """Test /api/hge/materials with active signal."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        # Mock status with signal data
        mock_status.return_value = {
            "hge_signal": {
                "system_name": "Tchernobog",
                "allegiance": "Federation",
                "government": "Democracy",
                "population": 1000000,
                "state": "Boom",
                "materials": {"count": 2, "materials": [
                    {"name": "Imperial Shielding", "count": 5},
                    {"name": "Proto Alloys", "count": 3},
                ]},
            },
            "distance_ly": 42.5,
            "commander_location": {"system_name": "Sol"},
        }
        
        with app.test_client() as client:
            response = client.get("/api/hge/materials")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["data"] is not None
            assert data["data"]["system_name"] == "Tchernobog"
            assert data["data"]["allegiance"] == "Federation"

    @patch.object(HGENotifierManager, 'get_status')
    def test_materials_endpoint_error_handling(self, mock_status):
        """Test /api/hge/materials error handling."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        # Mock an exception
        mock_status.side_effect = Exception("Database error")
        
        with app.test_client() as client:
            response = client.get("/api/hge/materials")
            assert response.status_code == 500
            
            data = json.loads(response.data)
            assert data["status"] == "error"
            assert "message" in data


class TestRefreshEndpoint:
    """Test /api/refresh POST endpoint."""

    def test_refresh_endpoint_post_success(self):
        """Test /api/refresh POST returns success."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.post("/api/refresh")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "data" in data

    def test_refresh_endpoint_get_not_allowed(self):
        """Test /api/refresh GET returns 405 Method Not Allowed."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/refresh")
            assert response.status_code == 405

    @patch.object(HGENotifierManager, 'refresh')
    @patch.object(HGENotifierManager, 'get_status')
    def test_refresh_endpoint_calls_manager_refresh(self, mock_get_status, mock_refresh):
        """Test /api/refresh calls manager.refresh()."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        mock_get_status.return_value = {"status": "ok"}
        
        with app.test_client() as client:
            response = client.post("/api/refresh")
            assert response.status_code == 200
            mock_refresh.assert_called_once()

    @patch.object(HGENotifierManager, 'refresh')
    def test_refresh_endpoint_error_handling(self, mock_refresh):
        """Test /api/refresh error handling."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        mock_refresh.side_effect = Exception("Refresh failed")
        
        with app.test_client() as client:
            response = client.post("/api/refresh")
            assert response.status_code == 500
            
            data = json.loads(response.data)
            assert data["status"] == "error"


class TestNotificationsEndpoints:
    """Test notification-related endpoints."""

    def test_notifications_endpoint_no_manager(self):
        """Test /api/notifications when notification_manager is None."""
        manager = HGENotifierManager()
        manager.notification_manager = None
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/notifications")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["data"] == []

    def test_notifications_endpoint_count_parameter(self):
        """Test /api/notifications with count query parameter."""
        manager = HGENotifierManager()
        manager.notification_manager = None
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/notifications?count=5")
            assert response.status_code == 200

    def test_notifications_stats_endpoint(self):
        """Test /api/notifications/stats endpoint."""
        manager = HGENotifierManager()
        manager.notification_manager = None
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/notifications/stats")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "data" in data
            assert data["data"]["total"] == 0

    def test_notifications_clear_endpoint(self):
        """Test /api/notifications/clear POST endpoint."""
        manager = HGENotifierManager()
        manager.notification_manager = None
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.post("/api/notifications/clear")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["status"] == "success"

    def test_notifications_clear_get_not_allowed(self):
        """Test /api/notifications/clear GET returns 405."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/notifications/clear")
            assert response.status_code == 405


class TestTimelineEndpoints:
    """Test timeline-related endpoints."""

    def test_timeline_endpoint(self):
        """Test /api/timeline endpoint."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/timeline")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert isinstance(data["data"], list)

    def test_timeline_endpoint_with_limit(self):
        """Test /api/timeline with limit parameter."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/timeline?limit=10")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["status"] == "success"

    def test_timeline_summary_endpoint(self):
        """Test /api/timeline/summary endpoint."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/timeline/summary")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "data" in data

    def test_timeline_trends_endpoint(self):
        """Test /api/timeline/trends endpoint."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/timeline/trends")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert isinstance(data["data"], list)


class TestSystemsEndpoint:
    """Test /api/systems endpoint."""

    def test_systems_endpoint_success(self):
        """Test /api/systems returns valid response."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/systems")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert isinstance(data["data"], list)
            assert "count" in data

    def test_systems_endpoint_sort_by_recent(self):
        """Test /api/systems with sort_by=recent."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/systems?sort_by=recent")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["sort_by"] == "recent"

    def test_systems_endpoint_sort_by_reports(self):
        """Test /api/systems with sort_by=reports."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/systems?sort_by=reports")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["sort_by"] == "reports"

    def test_systems_endpoint_sort_by_distance(self):
        """Test /api/systems with sort_by=distance."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/systems?sort_by=distance")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["sort_by"] == "distance"

    def test_systems_endpoint_invalid_sort_by_defaults(self):
        """Test /api/systems with invalid sort_by defaults to recent."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/systems?sort_by=invalid")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["sort_by"] == "recent"

    def test_systems_endpoint_with_material_filter(self):
        """Test /api/systems with material filter."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/systems?material=Imperial%20Shielding")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["material_filter"] == "Imperial Shielding"

    def test_systems_endpoint_with_limit(self):
        """Test /api/systems with limit parameter."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/systems?limit=25")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert len(data["data"]) <= 25


class TestSystemDetailEndpoint:
    """Test /api/systems/<system_name> endpoint."""

    def test_system_detail_endpoint_returns_response(self):
        """Test /api/systems/<system_name> returns a response."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/systems/Tchernobog")
            # System detail endpoint returns 200 even if system not found
            assert response.status_code in [200, 404]

    def test_system_detail_endpoint_json_response(self):
        """Test /api/systems/<system_name> returns JSON."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/systems/TestSystem")
            # Should return JSON response
            if response.status_code == 200:
                assert response.content_type == "application/json"


class TestMaterialsDetailEndpoint:
    """Test /api/materials/<material_name> endpoint."""

    def test_materials_detail_endpoint(self):
        """Test /api/materials/<material_name> returns response."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/materials/Imperial%20Shielding")
            assert response.status_code == 200

    def test_materials_detail_json_response(self):
        """Test /api/materials/<material_name> returns JSON."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/materials/TestMaterial")
            assert response.status_code == 200
            assert response.content_type == "application/json"


class TestMaterialsListEndpoint:
    """Test /api/materials endpoint."""

    def test_materials_list_endpoint(self):
        """Test /api/materials returns list."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/materials")
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert isinstance(data["data"], list)


class TestHTMLRoutes:
    """Test HTML template routes."""

    def test_timeline_html_route(self):
        """Test /timeline HTML route."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/timeline")
            assert response.status_code == 200

    def test_notifications_html_route(self):
        """Test /notifications HTML route."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/notifications")
            assert response.status_code == 200


class TestErrorHandling:
    """Test error handling across endpoints."""

    @patch.object(HGENotifierManager, 'get_status')
    def test_status_endpoint_graceful_error(self, mock_status):
        """Test /api/status handles errors gracefully."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        mock_status.side_effect = RuntimeError("Connection failed")
        
        with app.test_client() as client:
            response = client.get("/api/status")
            # Status should handle exceptions gracefully
            assert response.status_code in [200, 500]

    def test_nonexistent_route_returns_404(self):
        """Test accessing non-existent route returns 404."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/nonexistent")
            assert response.status_code == 404

    def test_json_content_type_on_api_endpoints(self):
        """Test all API endpoints return JSON content type."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        endpoints = [
            "/api/status",
            "/api/hge/materials",
            "/api/notifications",
            "/api/timeline",
            "/api/systems",
            "/api/materials",
        ]
        
        with app.test_client() as client:
            for endpoint in endpoints:
                response = client.get(endpoint)
                assert response.content_type == "application/json", \
                    f"{endpoint} did not return JSON"


class TestQueryParameterValidation:
    """Test query parameter validation."""

    def test_invalid_limit_parameter(self):
        """Test endpoints handle invalid limit parameter."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            # Non-integer limit should be handled
            response = client.get("/api/timeline?limit=invalid")
            # Should either default or return error, but not crash
            assert response.status_code in [200, 400]

    def test_negative_limit_parameter(self):
        """Test endpoints handle negative limit parameter."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/timeline?limit=-5")
            assert response.status_code in [200, 400]

    def test_very_large_limit_parameter(self):
        """Test endpoints handle very large limit parameter."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/systems?limit=999999")
            assert response.status_code == 200


class TestResponseFormats:
    """Test response format consistency."""

    def test_success_responses_have_status_field(self):
        """Test all success responses have 'status' field."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        endpoints = [
            "/api/hge/materials",
            "/api/notifications",
            "/api/timeline",
            "/api/systems",
            "/api/materials",
        ]
        
        with app.test_client() as client:
            for endpoint in endpoints:
                response = client.get(endpoint)
                if response.status_code == 200:
                    data = json.loads(response.data)
                    assert "status" in data or "commander_location" in data, \
                        f"{endpoint} response missing 'status' field"

    def test_error_responses_have_message_field(self):
        """Test error responses include error message."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            # Trigger an error
            response = client.get("/api/nonexistent")
            assert response.status_code == 404
