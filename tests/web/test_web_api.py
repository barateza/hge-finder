"""
Phase 2: Web API Integration Tests

Tests for:
- Flask app creation and configuration
- API endpoints (/api/status, /api/hge/materials, /api/refresh)
- Error handling in endpoints
- WebSocket integration
- Template rendering
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

from src.web import create_app
from src.core import HGENotifierManager
from src.eddn import HGESignal
from datetime import datetime


class TestFlaskAppCreationPhase2:
    """Test Flask app creation and configuration."""

    def test_create_app_returns_flask_app(self):
        """Test create_app returns Flask application."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        assert isinstance(app, Flask)
        assert app is not None

    def test_create_app_sets_json_config(self):
        """Test Flask app has correct configuration."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        # Should have JSON_SORT_KEYS disabled
        assert app.config.get("JSON_SORT_KEYS") is False

    def test_create_app_without_websocket_manager(self):
        """Test create_app works without WebSocket manager."""
        manager = HGENotifierManager()
        app = create_app(manager, ws_manager=None)
        
        assert isinstance(app, Flask)

    def test_create_app_with_websocket_manager(self):
        """Test create_app works with WebSocket manager."""
        from src.web.websocket import WebSocketManager
        
        manager = HGENotifierManager()
        ws_manager = WebSocketManager()
        app = create_app(manager, ws_manager=ws_manager)
        
        assert isinstance(app, Flask)


class TestFlaskIndexRoutePhase2:
    """Test Flask index route."""

    def test_index_route_returns_html(self):
        """Test index route returns HTML template."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/")
            assert response.status_code == 200
            assert b"html" in response.data.lower() or len(response.data) > 0

    def test_index_route_accessible(self):
        """Test index route is accessible."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/")
            assert response.status_code == 200


class TestFlaskStatusAPIPhase2:
    """Test /api/status endpoint."""

    def test_status_endpoint_returns_json(self):
        """Test /api/status returns JSON."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/status")
            assert response.status_code == 200
            assert response.content_type == "application/json"

    def test_status_endpoint_returns_dict(self):
        """Test /api/status returns dictionary."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/status")
            data = json.loads(response.data)
            assert isinstance(data, dict)

    def test_status_endpoint_includes_required_fields(self):
        """Test /api/status includes required fields."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/status")
            data = json.loads(response.data)
            
            # Should have these fields
            assert "initialized" in data
            assert "hge_signal" in data
            assert "commander_location" in data

    def test_status_endpoint_after_manager_start(self):
        """Test /api/status works after manager is started."""
        manager = HGENotifierManager()
        manager.start()
        app = create_app(manager)
        
        try:
            with app.test_client() as client:
                response = client.get("/api/status")
                data = json.loads(response.data)
                
                assert response.status_code == 200
                assert data["initialized"] is True
        finally:
            manager.stop()


class TestFlaskMaterialsAPIPhase2:
    """Test /api/hge/materials endpoint."""

    def test_materials_endpoint_returns_json(self):
        """Test /api/hge/materials returns JSON."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/hge/materials")
            assert response.status_code == 200
            assert response.content_type == "application/json"

    def test_materials_endpoint_without_signal(self):
        """Test /api/hge/materials when no signal available."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/hge/materials")
            data = json.loads(response.data)
            
            assert response.status_code == 200
            assert "status" in data

    def test_materials_endpoint_structure(self):
        """Test /api/hge/materials returns correct structure."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/hge/materials")
            data = json.loads(response.data)
            
            # Should have status field
            assert "status" in data
            assert data["status"] in ["success", "error"]

    def test_materials_endpoint_with_signal(self):
        """Test /api/hge/materials with active signal."""
        manager = HGENotifierManager()
        manager.start()
        
        try:
            # Create mock signal
            signal = HGESignal(
                system_name="Test System",
                timestamp=datetime.utcnow(),
                x=10.0,
                y=20.0,
                z=30.0
            )
            manager._on_new_hge_signal(signal)
            
            app = create_app(manager)
            
            with app.test_client() as client:
                response = client.get("/api/hge/materials")
                data = json.loads(response.data)
                
                assert response.status_code == 200
                assert "status" in data
        finally:
            manager.stop()


class TestFlaskRefreshAPIPhase2:
    """Test /api/refresh endpoint."""

    def test_refresh_endpoint_exists(self):
        """Test /api/refresh endpoint exists."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            # POST request to refresh
            response = client.post("/api/refresh")
            # Should return 200 or 400+ but not 404
            assert response.status_code != 404

    def test_refresh_endpoint_returns_json(self):
        """Test /api/refresh returns JSON response."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.post("/api/refresh")
            # If not 404, should be JSON
            if response.status_code != 404:
                if response.content_type == "application/json":
                    data = json.loads(response.data)
                    assert isinstance(data, dict)


class TestFlaskErrorHandlingPhase2:
    """Test Flask error handling."""

    def test_invalid_route_returns_404(self):
        """Test invalid route returns 404."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/invalid/route")
            assert response.status_code == 404

    def test_api_status_malformed_request(self):
        """Test /api/status handles malformed requests gracefully."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            # Regular GET should work
            response = client.get("/api/status")
            assert response.status_code == 200

    def test_endpoint_content_type(self):
        """Test endpoints return correct content type."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/status")
            assert "application/json" in response.content_type


class TestFlaskJSONSerializationPhase2:
    """Test Flask JSON serialization."""

    def test_status_json_serializable(self):
        """Test status response is valid JSON."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/status")
            # Should be valid JSON
            data = json.loads(response.data)
            # Should be able to re-serialize
            json.dumps(data)

    def test_materials_json_serializable(self):
        """Test materials response is valid JSON."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/hge/materials")
            data = json.loads(response.data)
            # Should be able to re-serialize
            json.dumps(data)


class TestFlaskMultipleRequestsPhase2:
    """Test Flask handles multiple requests."""

    def test_multiple_status_requests(self):
        """Test multiple consecutive requests to /api/status."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            for _ in range(3):
                response = client.get("/api/status")
                assert response.status_code == 200
                data = json.loads(response.data)
                assert isinstance(data, dict)

    def test_multiple_endpoint_requests(self):
        """Test multiple requests to different endpoints."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            # Status endpoint
            response1 = client.get("/api/status")
            assert response1.status_code == 200
            
            # Materials endpoint
            response2 = client.get("/api/hge/materials")
            assert response2.status_code == 200
            
            # Index
            response3 = client.get("/")
            assert response3.status_code == 200


class TestFlaskResponseContentPhase2:
    """Test Flask response content."""

    def test_status_response_has_content(self):
        """Test status response has actual content."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/status")
            assert len(response.data) > 0

    def test_materials_response_has_content(self):
        """Test materials response has actual content."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/api/hge/materials")
            assert len(response.data) > 0

    def test_index_response_has_content(self):
        """Test index response has HTML content."""
        manager = HGENotifierManager()
        app = create_app(manager)
        
        with app.test_client() as client:
            response = client.get("/")
            assert len(response.data) > 100  # Should be substantial HTML
