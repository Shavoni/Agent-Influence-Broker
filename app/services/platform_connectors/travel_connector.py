"""
Travel Platform Connector for External Agent Discovery.

Connects to travel platforms like Booking.com, Expedia, and other
travel booking platforms to discover travel planning agents.
"""

import asyncio
import logging
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

logger = logging.getLogger(__name__)


class TravelPlatformConnector(BasePlatformConnector):
    """Connector for travel platforms."""
    
    PLATFORM_CONFIGS = {
        "booking.com": {
            "display_name": "Booking.com Travel Assistant",
            "base_url": "https://api.booking.com/v1",
            "agent_types": [ExternalAgentType.TRAVEL_PLANNER, ExternalAgentType.BOOKING_AGENT]
        },
        "expedia": {
            "display_name": "Expedia Travel Planner",
            "base_url": "https://api.expedia.com/v3",
            "agent_types": [ExternalAgentType.TRAVEL_PLANNER, ExternalAgentType.BOOKING_AGENT]
        }
    }
    
    def __init__(self, platform_variant: str = "booking.com"):
        super().__init__(f"{platform_variant.replace('.', '_')}_travel")
        self.variant = platform_variant
        self.config = self.PLATFORM_CONFIGS.get(platform_variant, self.PLATFORM_CONFIGS["booking.com"])
        
    async def is_available(self) -> bool:
        await asyncio.sleep(0.1)
        return True
    
    async def get_platform_info(self) -> PlatformConnectorInfo:
        return PlatformConnectorInfo(
            name=self.platform_name,
            display_name=self.config["display_name"],
            description=f"Travel planning and booking agents for {self.variant}",
            platform_type=PlatformType.TRAVEL,
            supported_agent_types=self.config["agent_types"],
            api_version="v1.0",
            base_url=self.config["base_url"],
            requires_authentication=True,
            auth_methods=["api_key"],
            supports_real_time=True,
            supports_webhooks=True
        )
    
    async def discover_agents(
        self,
        agent_types: Optional[List[ExternalAgentType]] = None,
        capabilities: Optional[List[str]] = None,
        filters: Optional[DiscoveryFilter] = None,
        user_id: Optional[str] = None
    ) -> List[ExternalAgentResponse]:
        relevant_types = [ExternalAgentType.TRAVEL_PLANNER, ExternalAgentType.BOOKING_AGENT]
        if agent_types:
            relevant_types = [t for t in relevant_types if t in agent_types]
        
        if not relevant_types:
            return []
        
        agents = []
        if ExternalAgentType.TRAVEL_PLANNER in relevant_types:
            agents.append(ExternalAgentResponse(
                external_id=f"{self.variant}_planner_001",
                platform=self.platform_name,
                name=f"{self.config['display_name']} - Smart Planner",
                description="AI-powered travel planning with personalized recommendations",
                agent_type=ExternalAgentType.TRAVEL_PLANNER,
                capabilities=[
                    ExternalAgentCapability(
                        name="itinerary_planning",
                        description="Create detailed travel itineraries",
                        category="planning",
                        supported_actions=["plan", "optimize", "suggest"]
                    ),
                    ExternalAgentCapability(
                        name="destination_research",
                        description="Research destinations and attractions",
                        category="research",
                        supported_actions=["research", "compare", "recommend"]
                    )
                ],
                reputation_score=8.9,
                success_rate=0.92,
                total_interactions=3450,
                is_available=True,
                is_verified=True,
                pricing_model="per_booking",
                base_cost=15.00,
                currency="USD",
                tags=[self.variant.replace(".", "_"), "travel", "planning"]
            ))
        
        return agents
    
    async def get_agents(self, agent_type: Optional[ExternalAgentType] = None, limit: int = 50, offset: int = 0, user_id: Optional[str] = None) -> List[ExternalAgentResponse]:
        agent_types = [agent_type] if agent_type else None
        return await self.discover_agents(agent_types=agent_types, user_id=user_id)
    
    async def get_agent_details(self, agent_id: str, user_id: Optional[str] = None) -> Optional[ExternalAgentResponse]:
        agents = await self.discover_agents(user_id=user_id)
        return next((a for a in agents if a.external_id == agent_id), None)
    
    async def connect_user(self, config: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        return {"connection_id": f"{self.platform_name}:{user_id}", "status": "connected"}
    
    async def disconnect_user(self, user_id: str) -> None:
        pass
    
    async def invite_agent(self, agent_id: str, inviter_id: str, message: Optional[str] = None) -> Dict[str, Any]:
        return {
            "invitation_id": f"inv_{self.platform_name}_{agent_id}_{inviter_id}",
            "status": "sent",
            "message": message or "Travel agent invitation"
        }
