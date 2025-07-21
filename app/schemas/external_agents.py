"""
External Agent schemas for discovery and integration.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class PlatformType(str, Enum):
    """Supported external platform types."""

    SHOPPING = "shopping"
    TRAVEL = "travel"
    FINANCE = "finance"
    SMART_HOME = "smart_home"
    SOCIAL = "social"
    PRODUCTIVITY = "productivity"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    EDUCATION = "education"
    CUSTOM = "custom"


class ExternalAgentType(str, Enum):
    """Types of external agents."""

    SHOPPING_ASSISTANT = "shopping_assistant"
    PRICE_COMPARISON = "price_comparison"
    TRAVEL_PLANNER = "travel_planner"
    BOOKING_AGENT = "booking_agent"
    INVESTMENT_ADVISOR = "investment_advisor"
    BUDGET_MANAGER = "budget_manager"
    SMART_HOME_CONTROLLER = "smart_home_controller"
    SOCIAL_MEDIA_MANAGER = "social_media_manager"
    TASK_AUTOMATION = "task_automation"
    CONTENT_CURATOR = "content_curator"
    HEALTH_TRACKER = "health_tracker"
    LEARNING_ASSISTANT = "learning_assistant"
    GENERIC = "generic"


class ConnectorStatus(str, Enum):
    """Status of platform connectors."""

    AVAILABLE = "available"
    CONNECTED = "connected"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class DiscoveryFilter(BaseModel):
    """Filters for agent discovery."""

    min_reputation: Optional[float] = Field(
        None, ge=0.0, le=10.0, description="Minimum reputation score"
    )
    max_reputation: Optional[float] = Field(
        None, ge=0.0, le=10.0, description="Maximum reputation score"
    )
    keywords: Optional[List[str]] = Field(
        default_factory=list, description="Keywords to search for"
    )
    location: Optional[str] = Field(
        None, description="Geographic location filter"
    )
    language: Optional[str] = Field(None, description="Preferred language")
    price_range: Optional[Dict[str, float]] = Field(
        None, description="Price range filter"
    )
    availability: Optional[bool] = Field(
        None, description="Filter by availability status"
    )
    verified_only: bool = Field(
        False, description="Only return verified agents"
    )


class ExternalAgentCapability(BaseModel):
    """External agent capability definition."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    category: str = Field(..., max_length=50)
    supported_actions: List[str] = Field(default_factory=list)
    api_endpoint: Optional[HttpUrl] = None
    authentication_required: bool = False


class ExternalAgentResponse(BaseModel):
    """Response model for external agent information."""

    external_id: str = Field(
        ..., description="Agent ID on the external platform"
    )
    platform: str = Field(..., description="Platform hosting the agent")
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., max_length=1000)
    agent_type: ExternalAgentType
    capabilities: List[ExternalAgentCapability] = Field(default_factory=list)

    # Performance metrics
    reputation_score: float = Field(0.0, ge=0.0, le=10.0)
    success_rate: float = Field(0.0, ge=0.0, le=1.0)
    total_interactions: int = Field(0, ge=0)
    average_response_time: Optional[float] = Field(
        None, description="Average response time in seconds"
    )

    # Availability and status
    is_available: bool = True
    is_verified: bool = False
    last_active: Optional[datetime] = None

    # Connection information
    api_endpoint: Optional[HttpUrl] = None
    webhook_url: Optional[HttpUrl] = None
    authentication_type: Optional[str] = None
    supported_protocols: List[str] = Field(default_factory=list)

    # Pricing and terms
    pricing_model: Optional[str] = None
    base_cost: Optional[float] = None
    currency: Optional[str] = None

    # Metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ExternalAgentDiscoveryRequest(BaseModel):
    """Request model for discovering external agents."""

    platforms: List[str] = Field(
        ..., min_items=1, description="Platforms to search"
    )
    agent_types: Optional[List[ExternalAgentType]] = Field(
        default_factory=list, description="Specific agent types to look for"
    )
    capabilities: Optional[List[str]] = Field(
        default_factory=list, description="Required capabilities"
    )
    filters: Optional[DiscoveryFilter] = None
    limit: int = Field(
        50, ge=1, le=500, description="Maximum number of results"
    )
    include_unavailable: bool = Field(
        False, description="Include unavailable agents"
    )


class PlatformConnectorInfo(BaseModel):
    """Information about a platform connector."""

    name: str = Field(..., description="Platform name")
    display_name: str = Field(..., description="Human-readable platform name")
    description: str = Field(..., description="Platform description")
    platform_type: PlatformType
    supported_agent_types: List[ExternalAgentType] = Field(
        default_factory=list
    )

    # API information
    api_version: str = Field(..., description="Supported API version")
    base_url: HttpUrl = Field(..., description="Platform base URL")
    documentation_url: Optional[HttpUrl] = None

    # Authentication requirements
    requires_authentication: bool = True
    auth_methods: List[str] = Field(default_factory=list)

    # Capabilities
    supports_real_time: bool = False
    supports_webhooks: bool = False
    rate_limit: Optional[Dict[str, int]] = None

    # Status
    is_active: bool = True
    maintenance_window: Optional[str] = None


class PlatformConnectorStatus(BaseModel):
    """Status of a platform connector."""

    platform_info: PlatformConnectorInfo
    status: ConnectorStatus
    last_checked: datetime
    error_message: Optional[str] = None
    available_agents_count: Optional[int] = None
    user_connected: bool = False
    connection_expires: Optional[datetime] = None


class PlatformConnectionConfig(BaseModel):
    """Configuration for connecting to a platform."""

    platform: str = Field(..., description="Platform name")
    auth_method: str = Field(..., description="Authentication method")
    credentials: Dict[str, str] = Field(
        ..., description="Authentication credentials"
    )
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    webhook_url: Optional[HttpUrl] = None
    enable_real_time: bool = False


class AgentInvitationRequest(BaseModel):
    """Request to invite an external agent."""

    agent_id: str = Field(..., description="External agent ID")
    platform: str = Field(..., description="Platform hosting the agent")
    invitation_type: str = Field(
        "negotiation", description="Type of invitation"
    )
    message: Optional[str] = Field(
        None, max_length=500, description="Optional invitation message"
    )
    proposed_terms: Optional[Dict[str, Any]] = Field(default_factory=dict)
    expiry_time: Optional[datetime] = None


class AgentInvitationResponse(BaseModel):
    """Response to an agent invitation."""

    invitation_id: str = Field(..., description="Unique invitation ID")
    status: str = Field(..., description="Invitation status")
    agent_response: Optional[str] = None
    response_time: Optional[datetime] = None
    next_steps: Optional[List[str]] = Field(default_factory=list)
    connection_details: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ExternalAgentRegistration(BaseModel):
    """Registration request for external agents to join the platform."""

    platform_agent_id: str = Field(
        ..., description="Agent ID on external platform"
    )
    platform_name: str = Field(..., description="External platform name")
    agent_name: str = Field(..., min_length=1, max_length=200)
    agent_type: ExternalAgentType
    capabilities: List[str] = Field(..., min_items=1)
    api_endpoint: HttpUrl = Field(..., description="Agent's API endpoint")
    webhook_url: Optional[HttpUrl] = None

    # Authentication
    auth_token: str = Field(..., description="Platform authentication token")
    auth_method: str = Field("bearer", description="Authentication method")

    # Platform verification
    platform_verification_token: str = Field(
        ..., description="Platform-provided verification token"
    )

    # Optional metadata
    description: Optional[str] = Field(None, max_length=1000)
    tags: List[str] = Field(default_factory=list)
    pricing_info: Optional[Dict[str, Any]] = Field(default_factory=dict)


# Aliases for backward compatibility
ExternalAgentCreate = ExternalAgentRegistration
ExternalAgentUpdate = ExternalAgentResponse
