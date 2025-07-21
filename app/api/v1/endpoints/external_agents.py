"""
External Agent Discovery API endpoints for Agent Influence Broker.

Enables discovery and integration with external agent platforms
including shopping assistants, travel bots, and finance agents.
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.core.exceptions import BusinessLogicError, NotFoundError
from app.models.user import User
from app.schemas.external_agents import (
    ExternalAgentDiscoveryRequest,
    ExternalAgentResponse,
    PlatformConnectorStatus,
    DiscoveryFilter
)
from app.services.external_discovery_service import ExternalDiscoveryService

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_discovery_service() -> ExternalDiscoveryService:
    """Get external discovery service dependency."""
    return ExternalDiscoveryService()


@router.post("/discover", response_model=List[ExternalAgentResponse])
async def discover_external_agents(
    discovery_request: ExternalAgentDiscoveryRequest,
    discovery_service: ExternalDiscoveryService = Depends(get_discovery_service),
    current_user: User = Depends(get_current_user),
) -> List[ExternalAgentResponse]:
    """
    Discover external agents across multiple platforms.
    
    Args:
        discovery_request: Search criteria and platform filters
        discovery_service: Discovery service dependency
        current_user: Authenticated user
        
    Returns:
        List of discovered external agents
    """
    try:
        logger.info(f"User {current_user.id} discovering external agents: {discovery_request.platforms}")
        
        discovered_agents = await discovery_service.discover_agents(
            platforms=discovery_request.platforms,
            agent_types=discovery_request.agent_types,
            capabilities=discovery_request.capabilities,
            filters=discovery_request.filters,
            user_id=current_user.id
        )
        
        logger.info(f"Discovered {len(discovered_agents)} external agents")
        return discovered_agents
        
    except Exception as e:
        logger.error(f"External agent discovery failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="External agent discovery failed"
        )


@router.get("/platforms", response_model=List[PlatformConnectorStatus])
async def get_available_platforms(
    discovery_service: ExternalDiscoveryService = Depends(get_discovery_service),
    current_user: User = Depends(get_current_user),
) -> List[PlatformConnectorStatus]:
    """
    Get list of available external platforms and their status.
    
    Returns:
        List of platform connectors with their availability status
    """
    try:
        platforms = await discovery_service.get_platform_status()
        return platforms
        
    except Exception as e:
        logger.error(f"Failed to get platform status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve platform status"
        )


@router.get("/platforms/{platform_name}/agents", response_model=List[ExternalAgentResponse])
async def get_platform_agents(
    platform_name: str,
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of agents to return"),
    offset: int = Query(0, ge=0, description="Number of agents to skip"),
    discovery_service: ExternalDiscoveryService = Depends(get_discovery_service),
    current_user: User = Depends(get_current_user),
) -> List[ExternalAgentResponse]:
    """
    Get agents from a specific platform.
    
    Args:
        platform_name: Name of the platform to query
        agent_type: Optional filter by agent type
        limit: Maximum number of results
        offset: Pagination offset
        discovery_service: Discovery service dependency
        current_user: Authenticated user
        
    Returns:
        List of agents from the specified platform
    """
    try:
        agents = await discovery_service.get_platform_agents(
            platform_name=platform_name,
            agent_type=agent_type,
            limit=limit,
            offset=offset,
            user_id=current_user.id
        )
        
        return agents
        
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Platform '{platform_name}' not found or not available"
        )
    except Exception as e:
        logger.error(f"Failed to get agents from platform {platform_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve platform agents"
        )


@router.post("/platforms/{platform_name}/connect")
async def connect_to_platform(
    platform_name: str,
    connection_config: Dict[str, Any],
    discovery_service: ExternalDiscoveryService = Depends(get_discovery_service),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Connect to an external platform with user credentials.
    
    Args:
        platform_name: Name of the platform to connect to
        connection_config: Platform-specific connection configuration
        discovery_service: Discovery service dependency
        current_user: Authenticated user
        
    Returns:
        Connection status and configuration
    """
    try:
        connection_result = await discovery_service.connect_to_platform(
            platform_name=platform_name,
            config=connection_config,
            user_id=current_user.id
        )
        
        logger.info(f"User {current_user.id} connected to platform {platform_name}")
        return connection_result
        
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Platform connection failed for {platform_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Platform connection failed"
        )


@router.delete("/platforms/{platform_name}/disconnect")
async def disconnect_from_platform(
    platform_name: str,
    discovery_service: ExternalDiscoveryService = Depends(get_discovery_service),
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Disconnect from an external platform.
    
    Args:
        platform_name: Name of the platform to disconnect from
        discovery_service: Discovery service dependency
        current_user: Authenticated user
        
    Returns:
        Disconnection confirmation
    """
    try:
        await discovery_service.disconnect_from_platform(
            platform_name=platform_name,
            user_id=current_user.id
        )
        
        logger.info(f"User {current_user.id} disconnected from platform {platform_name}")
        return {"message": f"Successfully disconnected from {platform_name}"}
        
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active connection to platform '{platform_name}'"
        )
    except Exception as e:
        logger.error(f"Platform disconnection failed for {platform_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Platform disconnection failed"
        )


@router.get("/agent/{external_agent_id}", response_model=ExternalAgentResponse)
async def get_external_agent_details(
    external_agent_id: str,
    platform: str = Query(..., description="Platform where the agent is hosted"),
    discovery_service: ExternalDiscoveryService = Depends(get_discovery_service),
    current_user: User = Depends(get_current_user),
) -> ExternalAgentResponse:
    """
    Get detailed information about a specific external agent.
    
    Args:
        external_agent_id: ID of the external agent
        platform: Platform hosting the agent
        discovery_service: Discovery service dependency
        current_user: Authenticated user
        
    Returns:
        Detailed external agent information
    """
    try:
        agent = await discovery_service.get_agent_details(
            agent_id=external_agent_id,
            platform=platform,
            user_id=current_user.id
        )
        
        if not agent:
            raise NotFoundError("External agent", external_agent_id)
            
        return agent
        
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"External agent '{external_agent_id}' not found on platform '{platform}'"
        )
    except Exception as e:
        logger.error(f"Failed to get external agent details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve external agent details"
        )


@router.post("/agent/{external_agent_id}/invite")
async def invite_external_agent(
    external_agent_id: str,
    platform: str = Query(..., description="Platform where the agent is hosted"),
    message: Optional[str] = None,
    discovery_service: ExternalDiscoveryService = Depends(get_discovery_service),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Send an invitation to an external agent to join negotiations.
    
    Args:
        external_agent_id: ID of the external agent
        platform: Platform hosting the agent
        message: Optional invitation message
        discovery_service: Discovery service dependency
        current_user: Authenticated user
        
    Returns:
        Invitation status and details
    """
    try:
        invitation_result = await discovery_service.invite_agent(
            agent_id=external_agent_id,
            platform=platform,
            inviter_id=current_user.id,
            message=message
        )
        
        logger.info(f"User {current_user.id} invited external agent {external_agent_id}")
        return invitation_result
        
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"External agent '{external_agent_id}' not found"
        )
    except BusinessLogicError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to invite external agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send agent invitation"
        )
