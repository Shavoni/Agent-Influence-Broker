"""Integration tests for the Agent Influence Broker API."""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.core.auth import create_access_token
from app.main import app
from app.models.agent import AgentCreate


class TestAgentEndpoints:
    """Integration tests for agent-related endpoints."""

    @pytest.fixture
    async def authenticated_client(self, mock_current_user):
        """Create authenticated test client."""
        token = create_access_token(data={"sub": mock_current_user["email"]})
        headers = {"Authorization": f"Bearer {token}"}

        async with AsyncClient(
            app=app, base_url="http://test", headers=headers
        ) as client:
            yield client

    @pytest.mark.asyncio
    async def test_create_agent_endpoint(self, authenticated_client):
        """Test agent creation through API endpoint."""
        # Arrange
        agent_data = {
            "name": "TestAgent",
            "description": "A test agent for negotiations",
            "capabilities": ["negotiation", "analysis"],
        }

        # Act
        with patch("app.services.agent_service.create_agent") as mock_create:
            mock_create.return_value = {
                "id": "agent-123",
                **agent_data,
                "status": "active",
                "reputation_score": 0.0,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            response = await authenticated_client.post(
                "/api/v1/agents", json=agent_data
            )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "TestAgent"
        assert data["capabilities"] == ["negotiation", "analysis"]

    @pytest.mark.asyncio
    async def test_get_agent_endpoint(self, authenticated_client, sample_agent_data):
        """Test agent retrieval through API endpoint."""
        # Act
        with patch("app.services.agent_service.get_agent_by_id") as mock_get:
            mock_get.return_value = sample_agent_data

            response = await authenticated_client.get("/api/v1/agents/agent-123")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "agent-123"
        assert data["name"] == "TestAgent"

    @pytest.mark.asyncio
    async def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/agents")
            assert response.status_code == 401


class TestNegotiationEndpoints:
    """Integration tests for negotiation-related endpoints."""

    @pytest.mark.asyncio
    async def test_create_negotiation_endpoint(self, authenticated_client):
        """Test negotiation creation through API endpoint."""
        # Arrange
        negotiation_data = {
            "initiator_id": "agent-123",
            "respondent_id": "agent-456",
            "terms": {"price": 1000, "delivery": "immediate"},
        }

        # Act
        with patch(
            "app.services.negotiation_service.create_negotiation"
        ) as mock_create:
            mock_create.return_value = {
                "id": "neg-123",
                **negotiation_data,
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            response = await authenticated_client.post(
                "/api/v1/negotiations", json=negotiation_data
            )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["initiator_id"] == "agent-123"
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_update_negotiation_status(self, authenticated_client):
        """Test negotiation status update through API endpoint."""
        # Act
        with patch(
            "app.services.negotiation_service.update_negotiation_status"
        ) as mock_update:
            mock_update.return_value = {"id": "neg-123", "status": "accepted"}

            response = await authenticated_client.patch(
                "/api/v1/negotiations/neg-123/status", json={"status": "accepted"}
            )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"


class TestInfluenceEndpoints:
    """Integration tests for influence metrics endpoints."""

    @pytest.mark.asyncio
    async def test_get_agent_influence_score(
        self, authenticated_client, sample_influence_data
    ):
        """Test retrieving agent influence score through API endpoint."""
        # Act
        with patch(
            "app.services.influence_service.calculate_influence_score"
        ) as mock_calc:
            mock_calc.return_value = sample_influence_data

            response = await authenticated_client.get(
                "/api/v1/agents/agent-123/influence"
            )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == "agent-123"
        assert data["influence_score"] == 85.5

    @pytest.mark.asyncio
    async def test_get_leaderboard(self, authenticated_client):
        """Test retrieving influence leaderboard through API endpoint."""
        # Arrange
        leaderboard_data = [
            {"agent_id": "agent-123", "influence_score": 95.5, "name": "TopAgent1"},
            {"agent_id": "agent-456", "influence_score": 92.0, "name": "TopAgent2"},
        ]

        # Act
        with patch(
            "app.services.influence_service.get_top_influential_agents"
        ) as mock_top:
            mock_top.return_value = leaderboard_data

            response = await authenticated_client.get(
                "/api/v1/influence/leaderboard?limit=10"
            )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["influence_score"] == 95.5
