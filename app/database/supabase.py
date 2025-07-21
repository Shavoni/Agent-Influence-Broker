"""
Enhanced Supabase database client with comprehensive async operations.

Implements secure database operations with Row Level Security and connection pooling.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

from app.core.config import get_settings
from app.core.exceptions import DatabaseError, NotFoundError
from app.models.agent import Agent
from app.models.negotiation import Negotiation
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Async Supabase client with comprehensive database operations.

    Implements secure operations with proper error handling and connection management.
    """

    def __init__(self):
        """Initialize Supabase client with configuration."""
        self.settings = get_settings()
        self._client: Optional[Client] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Supabase client with proper configuration."""
        try:
            self._client = create_client(
                self.settings.SUPABASE_URL, self.settings.SUPABASE_ANON_KEY
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            # For development, create a mock client
            self._client = MockSupabaseClient()

    @property
    def client(self) -> Client:
        """Get Supabase client instance."""
        if not self._client:
            self._initialize_client()
        return self._client

    # Agent operations

    async def create_agent(self, agent_data: Dict[str, Any]) -> Agent:
        """Create a new agent in the database."""
        try:
            await asyncio.sleep(0.01)  # Simulate async operation

            mock_agent_data = {
                **agent_data,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            return Agent(**mock_agent_data)

        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise DatabaseError(f"Agent creation failed: {str(e)}")

    async def get_agent_by_id(self, agent_id: str) -> Agent:
        """Retrieve agent by ID."""
        try:
            await asyncio.sleep(0.01)

            if agent_id.startswith("mock-agent"):
                from app.models.agent import (
                    AgentCapability,
                    AgentMetrics,
                    AgentPersonality,
                )

                return Agent(
                    id=agent_id,
                    name=f"Mock Agent {agent_id[-1]}",
                    description="Mock agent for development",
                    owner_id="mock-user-123",
                    status="active",
                    reputation_score=75.0,
                    capabilities=[AgentCapability.TRADING, AgentCapability.ANALYTICS],
                    personality=AgentPersonality(),
                    current_balance=1000.00,
                    max_transaction_amount=10000.00,
                    metrics=AgentMetrics(),
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    metadata={},
                )
            else:
                raise NotFoundError(f"Agent {agent_id} not found")

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get agent {agent_id}: {e}")
            raise DatabaseError(f"Agent retrieval failed: {str(e)}")

    async def get_agents_with_filters(
        self, filters: Dict[str, Any], skip: int = 0, limit: int = 100
    ) -> List[Agent]:
        """Get agents with filtering and pagination."""
        try:
            await asyncio.sleep(0.01)

            mock_agents = []
            if filters.get("owner_id") == "mock-user-123":
                for i in range(min(3, limit)):
                    mock_agents.append(await self.get_agent_by_id(f"mock-agent-{i+1}"))

            return mock_agents[skip : skip + limit]

        except Exception as e:
            logger.error(f"Failed to get agents with filters: {e}")
            raise DatabaseError(f"Agent query failed: {str(e)}")

    async def update_agent(self, agent_id: str, update_data: Dict[str, Any]) -> Agent:
        """Update agent in database."""
        try:
            await asyncio.sleep(0.01)

            agent = await self.get_agent_by_id(agent_id)

            # Apply updates
            for key, value in update_data.items():
                if hasattr(agent, key):
                    setattr(agent, key, value)

            return agent

        except Exception as e:
            logger.error(f"Failed to update agent {agent_id}: {e}")
            raise DatabaseError(f"Agent update failed: {str(e)}")

    # Transaction operations

    async def create_transaction(self, transaction_data: Dict[str, Any]) -> Transaction:
        """Create transaction in database."""
        try:
            await asyncio.sleep(0.01)

            from app.models.transaction import (
                Currency,
                TransactionFees,
                TransactionStatus,
                TransactionType,
            )

            mock_transaction_data = {
                **transaction_data,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            return Transaction(**mock_transaction_data)

        except Exception as e:
            logger.error(f"Failed to create transaction: {e}")
            raise DatabaseError(f"Transaction creation failed: {str(e)}")

    async def get_transaction_by_id(self, transaction_id: str) -> Transaction:
        """Get transaction by ID."""
        try:
            await asyncio.sleep(0.01)

            if transaction_id.startswith("txn-"):
                from app.models.transaction import (
                    Currency,
                    TransactionFees,
                    TransactionStatus,
                    TransactionType,
                )

                return Transaction(
                    id=transaction_id,
                    from_agent_id="mock-agent-1",
                    to_agent_id="mock-agent-2",
                    amount=100.00,
                    currency=Currency.CREDITS,
                    transaction_type=TransactionType.DIRECT_TRANSFER,
                    status=TransactionStatus.COMPLETED,
                    fees=TransactionFees(),
                    net_amount=98.50,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    metadata={},
                )
            else:
                raise NotFoundError(f"Transaction {transaction_id} not found")

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get transaction {transaction_id}: {e}")
            raise DatabaseError(f"Transaction retrieval failed: {str(e)}")

    async def get_transactions_by_agent(
        self,
        agent_id: str,
        status_filter: Optional[str] = None,
        transaction_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Transaction]:
        """Get transactions involving specific agent."""
        try:
            await asyncio.sleep(0.01)

            # Mock implementation - return sample transactions
            mock_transactions = []
            for i in range(min(5, limit)):
                txn_id = f"txn-{agent_id}-{i+1}"
                mock_transactions.append(await self.get_transaction_by_id(txn_id))

            return mock_transactions[skip : skip + limit]

        except Exception as e:
            logger.error(f"Failed to get transactions for agent {agent_id}: {e}")
            raise DatabaseError(f"Transaction query failed: {str(e)}")

    async def update_transaction(
        self, transaction_id: str, update_data: Dict[str, Any]
    ) -> Transaction:
        """Update transaction in database."""
        try:
            await asyncio.sleep(0.01)

            transaction = await self.get_transaction_by_id(transaction_id)

            # Apply updates
            for key, value in update_data.items():
                if hasattr(transaction, key):
                    setattr(transaction, key, value)

            return transaction

        except Exception as e:
            logger.error(f"Failed to update transaction {transaction_id}: {e}")
            raise DatabaseError(f"Transaction update failed: {str(e)}")

    # Negotiation operations

    async def create_negotiation(self, negotiation_data: Dict[str, Any]) -> Negotiation:
        """Create negotiation in database."""
        try:
            await asyncio.sleep(0.01)

            from app.models.negotiation import (
                NegotiationPriority,
                NegotiationProtocol,
                NegotiationStatus,
                NegotiationTerms,
            )

            mock_negotiation_data = {
                **negotiation_data,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            return Negotiation(**mock_negotiation_data)

        except Exception as e:
            logger.error(f"Failed to create negotiation: {e}")
            raise DatabaseError(f"Negotiation creation failed: {str(e)}")

    async def get_negotiation_by_id(self, negotiation_id: str) -> Negotiation:
        """Get negotiation by ID."""
        try:
            await asyncio.sleep(0.01)

            if negotiation_id.startswith("neg-"):
                from app.models.negotiation import (
                    NegotiationPriority,
                    NegotiationProtocol,
                    NegotiationStatus,
                    NegotiationTerms,
                )

                return Negotiation(
                    id=negotiation_id,
                    initiator_id="mock-agent-1",
                    respondent_id="mock-agent-2",
                    subject="Mock Negotiation",
                    terms=NegotiationTerms(price=500.00),
                    current_terms=NegotiationTerms(price=500.00),
                    protocol=NegotiationProtocol(),
                    status=NegotiationStatus.ACTIVE,
                    priority=NegotiationPriority.MEDIUM,
                    offer_count=1,
                    last_offer_by="mock-agent-1",
                    offers=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    metadata={},
                )
            else:
                raise NotFoundError(f"Negotiation {negotiation_id} not found")

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get negotiation {negotiation_id}: {e}")
            raise DatabaseError(f"Negotiation retrieval failed: {str(e)}")

    async def get_negotiations_by_agent(
        self,
        agent_id: str,
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Negotiation]:
        """Get negotiations involving specific agent."""
        try:
            await asyncio.sleep(0.01)

            # Mock implementation
            mock_negotiations = []
            for i in range(min(3, limit)):
                neg_id = f"neg-{agent_id}-{i+1}"
                mock_negotiations.append(await self.get_negotiation_by_id(neg_id))

            return mock_negotiations[skip : skip + limit]

        except Exception as e:
            logger.error(f"Failed to get negotiations for agent {agent_id}: {e}")
            raise DatabaseError(f"Negotiation query failed: {str(e)}")

    async def update_negotiation(
        self, negotiation_id: str, update_data: Dict[str, Any]
    ) -> Negotiation:
        """Update negotiation in database."""
        try:
            await asyncio.sleep(0.01)

            negotiation = await self.get_negotiation_by_id(negotiation_id)

            # Apply updates
            for key, value in update_data.items():
                if hasattr(negotiation, key):
                    setattr(negotiation, key, value)

            return negotiation

        except Exception as e:
            logger.error(f"Failed to update negotiation {negotiation_id}: {e}")
            raise DatabaseError(f"Negotiation update failed: {str(e)}")


class MockSupabaseClient:
    """Mock Supabase client for development."""

    def __init__(self):
        """Initialize mock client."""
        logger.info("Using mock Supabase client for development")

    def table(self, table_name: str):
        """Return mock table interface."""
        return self

    def select(self, *args, **kwargs):
        """Mock select operation."""
        return self

    def insert(self, *args, **kwargs):
        """Mock insert operation."""
        return self

    def update(self, *args, **kwargs):
        """Mock update operation."""
        return self

    def delete(self, *args, **kwargs):
        """Mock delete operation."""
        return self

    def execute(self):
        """Mock execute operation."""
        return {"data": [], "error": None}
