"""
External Agent Discovery Service for Agent Influence Broker.

Handles discovery, connection, and management of external agents
from various platforms including shopping, travel, and finance.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Set
from uuid import uuid4

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.core.exceptions import BusinessLogicError, NotFoundError
from app.schemas.external_agents import (
    ExternalAgentResponse,
    ExternalAgentType,
    PlatformConnectorStatus,
    PlatformConnectorInfo,
    PlatformType,
    ConnectorStatus,
    DiscoveryFilter,
    ExternalAgentCapability,
    PlatformConnectionConfig,
    AgentInvitationResponse
)
from app.services.platform_connectors import (
    ShoppingPlatformConnector,
    TravelPlatformConnector,
    FinancePlatformConnector,
    SmartHomePlatformConnector
)

logger = logging.getLogger(__name__)


class ExternalDiscoveryService:
    """Service for discovering and managing external agents."""
    
    def __init__(self):
        self.connectors = self._initialize_connectors()
        self.connection_cache = {}
        self.discovery_cache = {}
        self.cache_ttl = timedelta(minutes=15)
        
    def _initialize_connectors(self) -> Dict[str, Any]:
        """Initialize platform connectors."""
        return {
            "amazon_shopping": ShoppingPlatformConnector("amazon"),
            "ebay_shopping": ShoppingPlatformConnector("ebay"),
            "booking_travel": TravelPlatformConnector("booking.com"),
            "expedia_travel": TravelPlatformConnector("expedia"),
            "plaid_finance": FinancePlatformConnector("plaid"),
            "mint_finance": FinancePlatformConnector("mint"),
            "alexa_smart_home": SmartHomePlatformConnector("alexa"),
            "google_home": SmartHomePlatformConnector("google_home"),
        }
    
    async def discover_agents(
        self,
        platforms: List[str],
        agent_types: Optional[List[ExternalAgentType]] = None,
        capabilities: Optional[List[str]] = None,
        filters: Optional[DiscoveryFilter] = None,
        user_id: str = None
    ) -> List[ExternalAgentResponse]:
        """
        Discover external agents across multiple platforms.
        
        Args:
            platforms: List of platform names to search
            agent_types: Optional filter by agent types
            capabilities: Optional filter by capabilities
            filters: Additional discovery filters
            user_id: User requesting the discovery
            
        Returns:
            List of discovered external agents
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(platforms, agent_types, capabilities, filters)
            if cache_key in self.discovery_cache:
                cached_result, cache_time = self.discovery_cache[cache_key]
                if datetime.utcnow() - cache_time < self.cache_ttl:
                    logger.info(f"Returning cached discovery results for key: {cache_key}")
                    return cached_result
            
            discovered_agents = []
            
            # Discovery tasks for parallel execution
            discovery_tasks = []
            
            for platform in platforms:
                if platform in self.connectors:
                    task = self._discover_platform_agents(
                        platform, agent_types, capabilities, filters, user_id
                    )
                    discovery_tasks.append(task)
                else:
                    logger.warning(f"Platform '{platform}' not supported")
            
            # Execute discoveries in parallel
            platform_results = await asyncio.gather(*discovery_tasks, return_exceptions=True)
            
            # Combine results and handle exceptions
            for i, result in enumerate(platform_results):
                if isinstance(result, Exception):
                    logger.error(f"Discovery failed for platform {platforms[i]}: {result}")
                    continue
                    
                discovered_agents.extend(result)
            
            # Apply additional filtering
            filtered_agents = self._apply_filters(discovered_agents, filters)
            
            # Sort by reputation and availability
            sorted_agents = sorted(
                filtered_agents,
                key=lambda a: (a.is_available, a.reputation_score),
                reverse=True
            )
            
            # Cache the results
            self.discovery_cache[cache_key] = (sorted_agents, datetime.utcnow())
            
            logger.info(f"Discovered {len(sorted_agents)} external agents across {len(platforms)} platforms")
            return sorted_agents
            
        except Exception as e:
            logger.error(f"External agent discovery failed: {e}")
            raise BusinessLogicError(f"Discovery failed: {str(e)}")
    
    async def _discover_platform_agents(
        self,
        platform: str,
        agent_types: Optional[List[ExternalAgentType]],
        capabilities: Optional[List[str]],
        filters: Optional[DiscoveryFilter],
        user_id: str
    ) -> List[ExternalAgentResponse]:
        """Discover agents from a specific platform."""
        try:
            connector = self.connectors[platform]
            
            # Check if connector is available
            if not await connector.is_available():
                logger.warning(f"Platform {platform} is not available")
                return []
            
            # Perform platform-specific discovery
            agents = await connector.discover_agents(
                agent_types=agent_types,
                capabilities=capabilities,
                filters=filters,
                user_id=user_id
            )
            
            return agents
            
        except Exception as e:
            logger.error(f"Platform discovery failed for {platform}: {e}")
            return []
    
    def _apply_filters(
        self, 
        agents: List[ExternalAgentResponse], 
        filters: Optional[DiscoveryFilter]
    ) -> List[ExternalAgentResponse]:
        """Apply additional filters to discovered agents."""
        if not filters:
            return agents
        
        filtered = agents
        
        # Reputation filter
        if filters.min_reputation is not None:
            filtered = [a for a in filtered if a.reputation_score >= filters.min_reputation]
        
        if filters.max_reputation is not None:
            filtered = [a for a in filtered if a.reputation_score <= filters.max_reputation]
        
        # Keyword filter
        if filters.keywords:
            keyword_set = set(kw.lower() for kw in filters.keywords)
            filtered = [
                a for a in filtered 
                if any(kw in a.name.lower() or kw in a.description.lower() 
                      for kw in keyword_set)
            ]
        
        # Availability filter
        if filters.availability is not None:
            filtered = [a for a in filtered if a.is_available == filters.availability]
        
        # Verified only filter
        if filters.verified_only:
            filtered = [a for a in filtered if a.is_verified]
        
        return filtered
    
    def _generate_cache_key(
        self,
        platforms: List[str],
        agent_types: Optional[List[ExternalAgentType]],
        capabilities: Optional[List[str]],
        filters: Optional[DiscoveryFilter]
    ) -> str:
        """Generate cache key for discovery requests."""
        key_parts = [
            "|".join(sorted(platforms)),
            "|".join(sorted([t.value for t in agent_types])) if agent_types else "",
            "|".join(sorted(capabilities)) if capabilities else "",
            str(hash(str(filters.dict()) if filters else ""))
        ]
        return "|".join(key_parts)
    
    async def get_platform_status(self) -> List[PlatformConnectorStatus]:
        """Get status of all platform connectors."""
        status_list = []
        
        for platform_name, connector in self.connectors.items():
            try:
                # Get platform info
                platform_info = await connector.get_platform_info()
                
                # Check availability
                is_available = await connector.is_available()
                status = ConnectorStatus.AVAILABLE if is_available else ConnectorStatus.UNAVAILABLE
                
                # Get agent count if available
                agent_count = None
                try:
                    agent_count = await connector.get_agent_count()
                except:
                    pass
                
                status_item = PlatformConnectorStatus(
                    platform_info=platform_info,
                    status=status,
                    last_checked=datetime.utcnow(),
                    available_agents_count=agent_count,
                    user_connected=platform_name in self.connection_cache
                )
                
                status_list.append(status_item)
                
            except Exception as e:
                logger.error(f"Failed to get status for platform {platform_name}: {e}")
                
                # Create error status
                error_status = PlatformConnectorStatus(
                    platform_info=PlatformConnectorInfo(
                        name=platform_name,
                        display_name=platform_name.replace("_", " ").title(),
                        description="Platform connector",
                        platform_type=PlatformType.CUSTOM,
                        api_version="unknown",
                        base_url="https://unknown.com"
                    ),
                    status=ConnectorStatus.ERROR,
                    last_checked=datetime.utcnow(),
                    error_message=str(e)
                )
                status_list.append(error_status)
        
        return status_list
    
    async def get_platform_agents(
        self,
        platform_name: str,
        agent_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        user_id: str = None
    ) -> List[ExternalAgentResponse]:
        """Get agents from a specific platform."""
        if platform_name not in self.connectors:
            raise NotFoundError("Platform", platform_name)
        
        connector = self.connectors[platform_name]
        
        # Convert agent_type string to enum if provided
        agent_type_enum = None
        if agent_type:
            try:
                agent_type_enum = ExternalAgentType(agent_type)
            except ValueError:
                logger.warning(f"Invalid agent type: {agent_type}")
        
        agents = await connector.get_agents(
            agent_type=agent_type_enum,
            limit=limit,
            offset=offset,
            user_id=user_id
        )
        
        return agents
    
    async def connect_to_platform(
        self,
        platform_name: str,
        config: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Connect user to an external platform."""
        if platform_name not in self.connectors:
            raise NotFoundError("Platform", platform_name)
        
        connector = self.connectors[platform_name]
        
        try:
            connection_result = await connector.connect_user(config, user_id)
            
            # Cache the connection
            self.connection_cache[f"{platform_name}:{user_id}"] = {
                "config": config,
                "connected_at": datetime.utcnow(),
                "connection_id": connection_result.get("connection_id")
            }
            
            return connection_result
            
        except Exception as e:
            logger.error(f"Failed to connect to platform {platform_name}: {e}")
            raise BusinessLogicError(f"Platform connection failed: {str(e)}")
    
    async def disconnect_from_platform(
        self,
        platform_name: str,
        user_id: str
    ) -> None:
        """Disconnect user from an external platform."""
        connection_key = f"{platform_name}:{user_id}"
        
        if connection_key not in self.connection_cache:
            raise NotFoundError("Platform connection", connection_key)
        
        if platform_name in self.connectors:
            connector = self.connectors[platform_name]
            await connector.disconnect_user(user_id)
        
        # Remove from cache
        del self.connection_cache[connection_key]
    
    async def get_agent_details(
        self,
        agent_id: str,
        platform: str,
        user_id: str
    ) -> Optional[ExternalAgentResponse]:
        """Get detailed information about a specific external agent."""
        if platform not in self.connectors:
            raise NotFoundError("Platform", platform)
        
        connector = self.connectors[platform]
        agent = await connector.get_agent_details(agent_id, user_id)
        
        return agent
    
    async def invite_agent(
        self,
        agent_id: str,
        platform: str,
        inviter_id: str,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send invitation to external agent."""
        if platform not in self.connectors:
            raise NotFoundError("Platform", platform)
        
        connector = self.connectors[platform]
        
        invitation_result = await connector.invite_agent(
            agent_id=agent_id,
            inviter_id=inviter_id,
            message=message
        )
        
        return invitation_result
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all platform connectors."""
        health_status = {
            "service": "external_discovery",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "platforms": {}
        }
        
        for platform_name, connector in self.connectors.items():
            try:
                is_healthy = await connector.health_check()
                health_status["platforms"][platform_name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "last_checked": datetime.utcnow().isoformat()
                }
            except Exception as e:
                health_status["platforms"][platform_name] = {
                    "status": "error",
                    "error": str(e),
                    "last_checked": datetime.utcnow().isoformat()
                }
        
        # Overall service health
        platform_statuses = [p["status"] for p in health_status["platforms"].values()]
        if any(status == "error" for status in platform_statuses):
            health_status["status"] = "degraded"
        elif any(status == "unhealthy" for status in platform_statuses):
            health_status["status"] = "degraded"
        
        return health_status
