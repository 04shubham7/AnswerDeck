"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from src.api.server import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestChatEndpoint:
    """Test chat endpoint."""

    @patch('src.api.routes.chat.get_chat_service')
    def test_chat_success(self, mock_get_service, client):
        """Test successful chat request."""
        mock_service = Mock()
        mock_service.chat = Mock(return_value={
            "query": "test",
            "response": "response",
            "context": [],
            "context_count": 0
        })
        mock_get_service.return_value = mock_service
        
        response = client.post("/api/v1/chat/", json={"content": "test message"})
        assert response.status_code == 200
        assert response.json()["query"] == "test"

    @patch('src.api.routes.chat.get_chat_service')
    def test_chat_error(self, mock_get_service, client):
        """Test error handling."""
        mock_service = Mock()
        mock_service.chat = Mock(side_effect=Exception("API Error"))
        mock_get_service.return_value = mock_service
        
        response = client.post("/api/v1/chat/", json={"content": "test message"})
        assert response.status_code == 500

    @patch('src.api.routes.chat.get_search_service')
    def test_search_endpoint(self, mock_get_service, client):
        """Test search endpoint."""
        mock_service = Mock()
        mock_service.search = Mock(return_value=[])
        mock_get_service.return_value = mock_service
        
        response = client.get("/api/v1/chat/search?q=test")
        assert response.status_code == 200


class TestHealthEndpoint:
    """Test health endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_status_endpoint(self, client):
        """Test status endpoint."""
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        assert "api_version" in response.json()
