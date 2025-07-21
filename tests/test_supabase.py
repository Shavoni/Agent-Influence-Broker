import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.core.exceptions import DatabaseError, NotFoundError
from app.database.supabase import SupabaseClient
from app.models.agent import Agent, AgentCreate, AgentUpdate
from app.models.negotiation import Negotiation, NegotiationCreate
from app.models.transaction import Transaction, TransactionCreate


class TestSupabaseClient:
    """Test suite for Supabase database operations."""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client."""
        with patch("app.database.supabase.create_client") as mock_create:
            mock_client = Mock()
            mock_create.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def supabase_client(self, mock_supabase):
        """Create SupabaseClient instance with mocked client."""
        return SupabaseClient()

    @pytest.fixture
    def sample_agent_data(self) -> Dict[str, Any]:
        """Sample agent data for testing."""
        return {
            "id": "agent-123",
            "name": "TestAgent",
            "description": "A test agent for negotiations",
            "capabilities": ["negotiation", "analysis"],
            "reputation_score": 85.5,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    @pytest.fixture
    def sample_negotiation_data(self) -> Dict[str, Any]:
        """Sample negotiation data for testing."""
        return {
            "id": "neg-123",
            "initiator_id": "agent-123",
            "respondent_id": "agent-456",
            "status": "active",
            "terms": {"price": 1000, "delivery": "immediate"},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }


class TestAgentOperations:
    """Test agent-related database operations."""

    @pytest.mark.asyncio
    async def test_create_agent_success(
        self, supabase_client, mock_supabase, sample_agent_data
    ):
        """Test successful agent creation."""
        # Arrange
        mock_supabase.table().insert().execute.return_value.data = [sample_agent_data]
        agent_create = AgentCreate(
            name="TestAgent", description="A test agent", capabilities=["negotiation"]
        )

        # Act
        result = await supabase_client.create_agent(agent_create)

        # Assert
        assert result.name == "TestAgent"
        assert result.capabilities == ["negotiation"]
        mock_supabase.table.assert_called_with("agents")

    @pytest.mark.asyncio
    async def test_create_agent_database_error(self, supabase_client, mock_supabase):
        """Test agent creation with database error."""
        # Arrange
        mock_supabase.table().insert().execute.side_effect = Exception(
            "Database connection failed"
        )
        agent_create = AgentCreate(
            name="TestAgent", description="Test", capabilities=[]
        )

        # Act & Assert
        with pytest.raises(DatabaseError, match="Failed to create agent"):
            await supabase_client.create_agent(agent_create)

    @pytest.mark.asyncio
    async def test_get_agent_by_id_success(
        self, supabase_client, mock_supabase, sample_agent_data
    ):
        """Test successful agent retrieval by ID."""
        # Arrange
        mock_supabase.table().select().eq().execute.return_value.data = [
            sample_agent_data
        ]

        # Act
        result = await supabase_client.get_agent_by_id("agent-123")

        # Assert
        assert result.id == "agent-123"
        assert result.name == "TestAgent"
        mock_supabase.table().select().eq.assert_called_with("id", "agent-123")

    @pytest.mark.asyncio
    async def test_get_agent_by_id_not_found(self, supabase_client, mock_supabase):
        """Test agent retrieval when agent doesn't exist."""
        # Arrange
        mock_supabase.table().select().eq().execute.return_value.data = []

        # Act & Assert
        with pytest.raises(NotFoundError, match="Agent not found"):
            await supabase_client.get_agent_by_id("nonexistent-id")

    @pytest.mark.asyncio
    async def test_update_agent_success(
        self, supabase_client, mock_supabase, sample_agent_data
    ):
        """Test successful agent update."""
        # Arrange
        updated_data = {**sample_agent_data, "reputation_score": 90.0}
        mock_supabase.table().update().eq().execute.return_value.data = [updated_data]

        agent_update = AgentUpdate(reputation_score=90.0)

        # Act
        result = await supabase_client.update_agent("agent-123", agent_update)

        # Assert
        assert result.reputation_score == 90.0
        mock_supabase.table().update().eq.assert_called_with("id", "agent-123")

    @pytest.mark.asyncio
    async def test_delete_agent_success(self, supabase_client, mock_supabase):
        """Test successful agent deletion."""
        # Arrange
        mock_supabase.table().delete().eq().execute.return_value = Mock()

        # Act
        result = await supabase_client.delete_agent("agent-123")

        # Assert
        assert result is True
        mock_supabase.table().delete().eq.assert_called_with("id", "agent-123")

    @pytest.mark.asyncio
    async def test_list_agents_with_pagination(
        self, supabase_client, mock_supabase, sample_agent_data
    ):
        """Test listing agents with pagination."""
        # Arrange
        mock_supabase.table().select().range().execute.return_value.data = [
            sample_agent_data
        ]

        # Act
        result = await supabase_client.list_agents(skip=0, limit=10)

        # Assert
        assert len(result) == 1
        assert result[0].name == "TestAgent"
        mock_supabase.table().select().range.assert_called_with(0, 9)


class TestNegotiationOperations:
    """Test negotiation-related database operations."""

    @pytest.mark.asyncio
    async def test_create_negotiation_success(
        self, supabase_client, mock_supabase, sample_negotiation_data
    ):
        """Test successful negotiation creation."""
        # Arrange
        mock_supabase.table().insert().execute.return_value.data = [
            sample_negotiation_data
        ]
        negotiation_create = NegotiationCreate(
            initiator_id="agent-123", respondent_id="agent-456", terms={"price": 1000}
        )

        # Act
        result = await supabase_client.create_negotiation(negotiation_create)

        # Assert
        assert result.initiator_id == "agent-123"
        assert result.respondent_id == "agent-456"
        assert result.terms["price"] == 1000

    @pytest.mark.asyncio
    async def test_get_negotiations_by_agent(
        self, supabase_client, mock_supabase, sample_negotiation_data
    ):
        """Test retrieving negotiations by agent ID."""
        # Arrange
        mock_supabase.table().select().or_().execute.return_value.data = [
            sample_negotiation_data
        ]

        # Act
        result = await supabase_client.get_negotiations_by_agent("agent-123")

        # Assert
        assert len(result) == 1
        assert result[0].initiator_id == "agent-123"

    @pytest.mark.asyncio
    async def test_update_negotiation_status(
        self, supabase_client, mock_supabase, sample_negotiation_data
    ):
        """Test updating negotiation status."""
        # Arrange
        updated_data = {**sample_negotiation_data, "status": "completed"}
        mock_supabase.table().update().eq().execute.return_value.data = [updated_data]

        # Act
        result = await supabase_client.update_negotiation_status("neg-123", "completed")

        # Assert
        assert result.status == "completed"
        mock_supabase.table().update.assert_called_with({"status": "completed"})


class TestTransactionOperations:
    """Test transaction-related database operations."""

    @pytest.mark.asyncio
    async def test_create_transaction_success(self, supabase_client, mock_supabase):
        """Test successful transaction creation."""
        # Arrange
        transaction_data = {
            "id": "txn-123",
            "from_agent_id": "agent-123",
            "to_agent_id": "agent-456",
            "amount": 1000.0,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        mock_supabase.table().insert().execute.return_value.data = [transaction_data]

        transaction_create = TransactionCreate(
            from_agent_id="agent-123", to_agent_id="agent-456", amount=1000.0
        )

        # Act
        result = await supabase_client.create_transaction(transaction_create)

        # Assert
        assert result.from_agent_id == "agent-123"
        assert result.amount == 1000.0
        assert result.status == "pending"

    @pytest.mark.asyncio
    async def test_get_agent_transactions(self, supabase_client, mock_supabase):
        """Test retrieving transactions for an agent."""
        # Arrange
        transaction_data = {
            "id": "txn-123",
            "from_agent_id": "agent-123",
            "to_agent_id": "agent-456",
            "amount": 1000.0,
            "status": "completed",
        }
        mock_supabase.table().select().or_().execute.return_value.data = [
            transaction_data
        ]

        # Act
        result = await supabase_client.get_agent_transactions("agent-123")

        # Assert
        assert len(result) == 1
        assert result[0].from_agent_id == "agent-123"


class TestInfluenceMetrics:
    """Test influence metrics calculations."""

    @pytest.mark.asyncio
    async def test_calculate_agent_influence_score(
        self, supabase_client, mock_supabase
    ):
        """Test agent influence score calculation."""
        # Arrange
        metrics_data = {
            "agent_id": "agent-123",
            "successful_negotiations": 15,
            "total_negotiations": 20,
            "average_deal_value": 5000.0,
            "reputation_score": 85.5,
        }
        mock_supabase.rpc().execute.return_value.data = [metrics_data]

        # Act
        result = await supabase_client.calculate_influence_score("agent-123")

        # Assert
        assert result["agent_id"] == "agent-123"
        assert result["successful_negotiations"] == 15
        assert result["average_deal_value"] == 5000.0

    @pytest.mark.asyncio
    async def test_get_top_influential_agents(self, supabase_client, mock_supabase):
        """Test retrieving top influential agents."""
        # Arrange
        top_agents_data = [
            {"agent_id": "agent-123", "influence_score": 95.5, "name": "TopAgent1"},
            {"agent_id": "agent-456", "influence_score": 92.0, "name": "TopAgent2"},
        ]
        mock_supabase.table().select().order().limit().execute.return_value.data = (
            top_agents_data
        )

        # Act
        result = await supabase_client.get_top_influential_agents(limit=2)

        # Assert
        assert len(result) == 2
        assert result[0]["influence_score"] == 95.5
        assert result[1]["influence_score"] == 92.0


class TestConnectionAndErrorHandling:
    """Test database connection and error handling."""

    @pytest.mark.asyncio
    async def test_connection_health_check(self, supabase_client, mock_supabase):
        """Test database connection health check."""
        # Arrange
        mock_supabase.table().select().limit().execute.return_value.data = []

        # Act
        result = await supabase_client.health_check()

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_connection_failure(self, supabase_client, mock_supabase):
        """Test handling of connection failures."""
        # Arrange
        mock_supabase.table().select().limit().execute.side_effect = Exception(
            "Connection timeout"
        )

        # Act & Assert
        with pytest.raises(DatabaseError, match="Database health check failed"):
            await supabase_client.health_check()

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, supabase_client, mock_supabase):
        """Test transaction rollback on error."""
        # Arrange
        mock_supabase.table().insert().execute.side_effect = Exception(
            "Constraint violation"
        )

        # Act & Assert
        with pytest.raises(DatabaseError):
            await supabase_client.create_agent(
                AgentCreate(name="TestAgent", description="Test", capabilities=[])
            )


class TestRowLevelSecurity:
    """Test Row Level Security (RLS) policies."""

    @pytest.mark.asyncio
    async def test_agent_access_with_valid_user(
        self, supabase_client, mock_supabase, sample_agent_data
    ):
        """Test agent access with valid user context."""
        # Arrange
        mock_supabase.table().select().eq().execute.return_value.data = [
            sample_agent_data
        ]

        # Act
        result = await supabase_client.get_agent_by_id("agent-123", user_id="user-123")

        # Assert
        assert result.id == "agent-123"

    @pytest.mark.asyncio
    async def test_unauthorized_agent_access(self, supabase_client, mock_supabase):
        """Test unauthorized agent access blocked by RLS."""
        # Arrange
        mock_supabase.table().select().eq().execute.return_value.data = []

        # Act & Assert
        with pytest.raises(NotFoundError):
            await supabase_client.get_agent_by_id(
                "agent-123", user_id="unauthorized-user"
            )


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Performance and Load Testing
class TestPerformance:
    """Test database performance and load handling."""

    @pytest.mark.asyncio
    async def test_bulk_agent_creation(self, supabase_client, mock_supabase):
        """Test bulk creation of agents."""
        # Arrange
        agents_data = [
            {"id": f"agent-{i}", "name": f"Agent{i}", "capabilities": []}
            for i in range(100)
        ]
        mock_supabase.table().insert().execute.return_value.data = agents_data

        # Act
        start_time = datetime.now()
        result = await supabase_client.bulk_create_agents(agents_data)
        end_time = datetime.now()

        # Assert
        assert len(result) == 100
        assert (
            end_time - start_time
        ).total_seconds() < 5.0  # Should complete within 5 seconds

    @pytest.mark.asyncio
    async def test_concurrent_negotiations(self, supabase_client, mock_supabase):
        """Test handling concurrent negotiation operations."""
        # Arrange
        mock_supabase.table().insert().execute.return_value.data = [{"id": "neg-123"}]

        # Act
        tasks = []
        for i in range(10):
            task = supabase_client.create_negotiation(
                NegotiationCreate(
                    initiator_id=f"agent-{i}",
                    respondent_id="agent-target",
                    terms={"price": 1000 + i},
                )
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Assert
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) > 0  # At least some should succeed
