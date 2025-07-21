"""
Finance Platform Connector for External Agent Discovery.
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.schemas.external_agents import (
    ExternalAgentResponse,
    ExternalAgentType,
    PlatformConnectorInfo,
    PlatformType,
    DiscoveryFilter,
    ExternalAgentCapability
)
from .base_connector import BasePlatformConnector


class FinancePlatformConnector(BasePlatformConnector):
    """Connector for finance platforms."""
    
    def __init__(self, platform_variant: str = "plaid"):
        super().__init__(f"{platform_variant}_finance")
        self.variant = platform_variant
        
    async def is_available(self) -> bool:
        await asyncio.sleep(0.1)
        return True
    
    async def get_platform_info(self) -> PlatformConnectorInfo:
        return PlatformConnectorInfo(
            name=self.platform_name,
            display_name=f"{self.variant.title()} Finance Assistant",
            description=f"Financial management agents for {self.variant}",
            platform_type=PlatformType.FINANCE,
            supported_agent_types=[ExternalAgentType.INVESTMENT_ADVISOR, ExternalAgentType.BUDGET_MANAGER],
            api_version="v1.0",
            base_url=f"https://api.{self.variant}.com/v1",
            requires_authentication=True,
            auth_methods=["oauth2"]
        )
    
    async def discover_agents(self, agent_types: Optional[List[ExternalAgentType]] = None, capabilities: Optional[List[str]] = None, filters: Optional[DiscoveryFilter] = None, user_id: Optional[str] = None) -> List[ExternalAgentResponse]:
        return [
            ExternalAgentResponse(
                external_id=f"{self.variant}_advisor_001",
                platform=self.platform_name,
                name=f"{self.variant.title()} Investment Advisor",
                description="AI-powered investment advice and portfolio management",
                agent_type=ExternalAgentType.INVESTMENT_ADVISOR,
                reputation_score=9.1,
                success_rate=0.88,
                total_interactions=2340,
                is_available=True,
                tags=[self.variant, "finance", "investment"]
            )
        ]
    
    async def get_agents(self, agent_type: Optional[ExternalAgentType] = None, limit: int = 50, offset: int = 0, user_id: Optional[str] = None) -> List[ExternalAgentResponse]:
        return await self.discover_agents(agent_types=[agent_type] if agent_type else None, user_id=user_id)
    
    async def get_agent_details(self, agent_id: str, user_id: Optional[str] = None) -> Optional[ExternalAgentResponse]:
        agents = await self.discover_agents(user_id=user_id)
        return next((a for a in agents if a.external_id == agent_id), None)
    
    async def connect_user(self, config: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        return {"connection_id": f"{self.platform_name}:{user_id}", "status": "connected"}
    
    async def disconnect_user(self, user_id: str) -> None:
        pass
    
    async def invite_agent(self, agent_id: str, inviter_id: str, message: Optional[str] = None) -> Dict[str, Any]:
        return {"invitation_id": f"inv_{self.platform_name}_{agent_id}_{inviter_id}", "status": "sent"}
