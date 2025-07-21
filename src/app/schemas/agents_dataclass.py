"""
Agent schemas using dataclasses for Python 3.14 compatibility
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


@dataclass
class AgentCapability:
    """Agent capability definition"""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentCreate:
    """Schema for creating a new agent"""
    name: str
    description: Optional[str]
    agent_type: str
    capabilities: List[AgentCapability] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    api_endpoint: Optional[str] = None
    webhook_url: Optional[str] = None
    api_key: Optional[str] = None

    def __post_init__(self):
        # Validation
        if not self.name or len(self.name) > 255:
            raise ValueError("Name must be 1-255 characters")
        
        allowed_types = ['trading', 'negotiation', 'influence', 'service', 'analytics']
        if self.agent_type not in allowed_types:
            raise ValueError(f'Agent type must be one of: {allowed_types}')


@dataclass
class AgentUpdate:
    """Schema for updating an agent"""
    name: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[List[AgentCapability]] = None
    metadata: Optional[Dict[str, Any]] = None
    api_endpoint: Optional[str] = None
    webhook_url: Optional[str] = None
    is_active: Optional[bool] = None


@dataclass
class AgentResponse:
    """Schema for agent response"""
    id: uuid.UUID
    name: str
    description: Optional[str]
    agent_type: str
    owner_id: str
    capabilities: List[AgentCapability]
    metadata: Dict[str, Any]
    reputation_score: float
    influence_score: float
    success_rate: float
    total_negotiations: int
    successful_negotiations: int
    is_active: bool
    is_verified: bool
    api_endpoint: Optional[str]
    webhook_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_active: Optional[datetime]


@dataclass
class AgentSummary:
    """Compact agent summary schema"""
    id: uuid.UUID
    name: str
    agent_type: str
    reputation_score: float
    influence_score: float
    is_active: bool
    is_verified: bool


@dataclass
class AgentStats:
    """Agent statistics schema"""
    total_negotiations: int
    successful_negotiations: int
    success_rate: float
    average_satisfaction: float
    reputation_score: float
    influence_score: float
    last_30_days_activity: int
    total_earnings: float
    total_spent: float


@dataclass
class AgentListResponse:
    """Schema for paginated agent list response"""
    agents: List[AgentSummary]
    total: int
    page: int
    size: int
    pages: int


@dataclass
class AgentSearchFilters:
    """Schema for agent search filters"""
    agent_type: Optional[str] = None
    min_reputation: Optional[float] = None
    max_reputation: Optional[float] = None
    min_influence: Optional[float] = None
    max_influence: Optional[float] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    capabilities: Optional[List[str]] = None
