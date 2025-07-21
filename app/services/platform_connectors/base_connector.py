"""
Base Platform Connector for External Agent Discovery.

Abstract base class for all platform connectors.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.schemas.external_agents import (
    DiscoveryFilter,
    ExternalAgentResponse,
    ExternalAgentType,
    PlatformConnectorInfo,
)


class BasePlatformConnector(ABC):
    """Abstract base class for platform connectors."""

    def __init__(self, platform_name: str):
        self.platform_name = platform_name
        self.is_connected = False
        self.last_health_check = None

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the platform is available."""

    @abstractmethod
    async def get_platform_info(self) -> PlatformConnectorInfo:
        """Get information about the platform."""

    @abstractmethod
    async def discover_agents(
        self,
        agent_types: Optional[List[ExternalAgentType]] = None,
        capabilities: Optional[List[str]] = None,
        filters: Optional[DiscoveryFilter] = None,
        user_id: Optional[str] = None,
    ) -> List[ExternalAgentResponse]:
        """Discover agents on the platform."""

    @abstractmethod
    async def get_agents(
        self,
        agent_type: Optional[ExternalAgentType] = None,
        limit: int = 50,
        offset: int = 0,
        user_id: Optional[str] = None,
    ) -> List[ExternalAgentResponse]:
        """Get agents from the platform."""

    @abstractmethod
    async def get_agent_details(
        self, agent_id: str, user_id: Optional[str] = None
    ) -> Optional[ExternalAgentResponse]:
        """Get detailed information about a specific agent."""

    @abstractmethod
    async def connect_user(
        self, config: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        """Connect a user to the platform."""

    @abstractmethod
    async def disconnect_user(self, user_id: str) -> None:
        """Disconnect a user from the platform."""

    @abstractmethod
    async def invite_agent(
        self, agent_id: str, inviter_id: str, message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Invite an agent to join negotiations."""

    async def get_agent_count(self) -> Optional[int]:
        """Get total number of available agents (optional)."""
        return None

    async def health_check(self) -> bool:
        """Perform health check on the platform connector."""
        try:
            available = await self.is_available()
            self.last_health_check = datetime.utcnow()
            return available
        except Exception:
            return False

    def _create_mock_agent(
        self,
        agent_id: str,
        name: str,
        agent_type: ExternalAgentType,
        reputation: float = 8.5,
    ) -> ExternalAgentResponse:
        """Create a mock agent for testing/demo purposes."""
        return ExternalAgentResponse(
            external_id=agent_id,
            platform=self.platform_name,
            name=name,
            description=f"Mock {agent_type.value} agent from {self.platform_name}",
            agent_type=agent_type,
            reputation_score=reputation,
            success_rate=0.85,
            total_interactions=150,
            is_available=True,
            is_verified=True,
            last_active=datetime.utcnow(),
            supported_protocols=["REST", "WebSocket"],
            pricing_model="per_transaction",
            base_cost=0.10,
            currency="USD",
            tags=[agent_type.value, self.platform_name],
        )
