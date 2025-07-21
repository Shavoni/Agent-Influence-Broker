"""
Agent Influence Broker - Agent Schemas

Comprehensive Pydantic models for agent management, validation,
and API request/response handling following project architecture.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class AgentStatus(str, Enum):
    """Agent status enumeration for lifecycle management."""

    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class NegotiationStyle(str, Enum):
    """Negotiation style enumeration for agent behavior configuration."""

    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    COOPERATIVE = "cooperative"
    ANALYTICAL = "analytical"
    ADAPTIVE = "adaptive"


class ExperienceLevel(str, Enum):
    """Experience level enumeration for agent capabilities."""

    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


class AgentCapability(BaseModel):
    """Individual agent capability with proficiency scoring."""

    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=50)
    proficiency: float = Field(..., ge=0.0, le=1.0)
    certified: bool = False
    acquired_date: Optional[datetime] = None


class AgentSpecialization(BaseModel):
    """Agent specialization area with expertise metrics."""

    domain: str = Field(..., min_length=1, max_length=100)
    expertise_level: float = Field(..., ge=0.0, le=1.0)
    years_experience: Optional[int] = Field(None, ge=0, le=50)
    certifications: List[str] = []


class AgentCreateRequest(BaseModel):
    """Request model for agent creation with comprehensive validation."""

    name: str = Field(
        ..., min_length=3, max_length=100, description="Agent display name"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Agent description and purpose"
    )
    capabilities: List[AgentCapability] = Field(
        default_factory=list, description="Agent capabilities and proficiencies"
    )
    specializations: List[AgentSpecialization] = Field(
        default_factory=list, description="Agent specialization domains"
    )
    experience_level: ExperienceLevel = Field(
        default=ExperienceLevel.NOVICE, description="Overall experience level"
    )
    negotiation_style: NegotiationStyle = Field(
        default=NegotiationStyle.BALANCED, description="Default negotiation approach"
    )
    max_concurrent_negotiations: int = Field(
        default=5, ge=1, le=50, description="Maximum simultaneous negotiations"
    )
    min_transaction_value: float = Field(
        default=0.01, ge=0.0, description="Minimum acceptable transaction value"
    )
    max_transaction_value: float = Field(
        default=1000.0, ge=0.01, description="Maximum transaction value limit"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate agent name meets requirements."""
        if not v.strip():
            raise ValueError("Agent name cannot be empty")
        if any(char in v for char in ["<", ">", "&", '"', "'"]):
            raise ValueError("Agent name contains invalid characters")
        return v.strip()

    @model_validator(mode='after')
    def validate_transaction_values(self):
        """Validate transaction value constraints."""
        min_val = self.min_transaction_value
        max_val = self.max_transaction_value

        if min_val >= max_val:
            raise ValueError(
                "min_transaction_value must be less than max_transaction_value"
            )

        return self


class AgentUpdateRequest(BaseModel):
    """Request model for agent updates with optional fields."""

    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    capabilities: Optional[List[AgentCapability]] = None
    specializations: Optional[List[AgentSpecialization]] = None
    experience_level: Optional[ExperienceLevel] = None
    negotiation_style: Optional[NegotiationStyle] = None
    max_concurrent_negotiations: Optional[int] = Field(None, ge=1, le=50)
    min_transaction_value: Optional[float] = Field(None, ge=0.0)
    max_transaction_value: Optional[float] = Field(None, ge=0.01)
    is_available: Optional[bool] = None


class AgentResponse(BaseModel):
    """Response model for agent data with comprehensive metadata."""

    id: str
    name: str
    description: Optional[str]
    status: AgentStatus
    owner_id: str
    capabilities: List[AgentCapability]
    specializations: List[AgentSpecialization]
    experience_level: ExperienceLevel
    negotiation_style: NegotiationStyle

    # Performance metrics
    reputation_score: float = Field(..., ge=0.0, le=1.0)
    influence_score: float = Field(..., ge=0.0, le=1.0)
    success_rate: float = Field(..., ge=0.0, le=1.0)
    total_negotiations: int = Field(..., ge=0)
    completed_negotiations: int = Field(..., ge=0)

    # Configuration
    max_concurrent_negotiations: int
    min_transaction_value: float
    max_transaction_value: float
    is_available: bool

    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_active: Optional[datetime]

    # Computed properties
    reputation_tier: str
    active_negotiations: int = 0

    class Config:
        """Pydantic configuration for optimal serialization."""

        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat(), UUID: str}


class AgentListResponse(BaseModel):
    """Response model for paginated agent listings."""

    agents: List[AgentResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


class AgentMetrics(BaseModel):
    """Detailed agent performance metrics and analytics."""

    agent_id: str
    reputation_score: float
    influence_score: float
    success_rate: float
    total_negotiations: int
    completed_negotiations: int
    failed_negotiations: int
    average_negotiation_time: Optional[float]
    total_value_transacted: float
    average_transaction_value: float
    peer_ratings: Dict[str, float]
    performance_trend: Dict[str, Any]
    last_updated: datetime


class AgentSearchRequest(BaseModel):
    """Request model for agent search and filtering."""

    query: Optional[str] = None
    status: Optional[List[AgentStatus]] = None
    experience_level: Optional[List[ExperienceLevel]] = None
    negotiation_style: Optional[List[NegotiationStyle]] = None
    min_reputation: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_reputation: Optional[float] = Field(None, ge=0.0, le=1.0)
    capabilities: Optional[List[str]] = None
    specializations: Optional[List[str]] = None
    available_only: bool = False
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
