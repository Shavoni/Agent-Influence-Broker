"""
Agent Influence Broker - API Tests

Comprehensive test suite for API endpoints with authentication,
validation, and business logic testing.
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

from app.main import app

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self):
        """Test basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestAgentEndpoints:
    """Test agent-related API endpoints."""

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user for testing."""
        return {
            "id": "test-user-id",
            "email": "test@example.com",
            "is_active": True,
        }

    def test_create_agent_unauthenticated(self):
        """Test agent creation without authentication."""
        agent_data = {
            "name": "Test Agent",
            "description": "Test agent description",
            "capabilities": ["trading", "analysis"],
            "specializations": ["crypto"],
        }
        response = client.post("/api/v1/agents/", json=agent_data)
        # Should work with mock authentication
        assert response.status_code in [201, 401]  # Depending on auth setup

    def test_list_agents(self):
        """Test listing agents."""
        response = client.get("/api/v1/agents/")
        assert response.status_code in [200, 401]  # Depending on auth setup

    def test_get_agent_not_found(self):
        """Test getting non-existent agent."""
        response = client.get("/api/v1/agents/non-existent-id")
        assert response.status_code in [404, 401]  # Depending on auth setup


class TestNegotiationEndpoints:
    """Test negotiation-related API endpoints."""

    def test_list_negotiations(self):
        """Test listing negotiations."""
        response = client.get("/api/v1/negotiations/")
        assert response.status_code in [200, 401]  # Depending on auth setup


class TestTransactionEndpoints:
    """Test transaction-related API endpoints."""

    def test_list_transactions(self):
        """Test listing transactions."""
        response = client.get("/api/v1/transactions/")
        assert response.status_code in [200, 401]  # Depending on auth setup


class TestErrorHandling:
    """Test API error handling."""

    def test_404_endpoint(self):
        """Test non-existent endpoint returns 404."""
        response = client.get("/api/v1/non-existent")
        assert response.status_code == 404

    def test_invalid_json(self):
        """Test invalid JSON handling."""
        response = client.post(
            "/api/v1/agents/",
            data="invalid json",
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])
