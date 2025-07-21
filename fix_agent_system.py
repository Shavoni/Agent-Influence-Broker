"""
Agent Influence Broker - Agent System Setup

Implements agent models, schemas, and service layer following
project architecture and async/await patterns.
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def create_agent_models() -> None:
    """Create agent database models."""

    agent_models_content = '''"""
Agent Influence Broker - Agent Models

Implements agent database models with capabilities, reputation,
and performance tracking following Supabase RLS patterns.
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AgentStatus(str, Enum):
    """Agent status enumeration for lifecycle management."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class Agent(Base):
    """
    Agent model with comprehensive capability and reputation tracking.
    
    Implements sophisticated agent management following project
    architecture with performance analytics and security validations.
    """
    __tablename__ = "agents"
    
    # Primary identification
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(20), default=AgentStatus.PENDING, index=True)
    
    # Owner relationship
    owner_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    owner = relationship("User", back_populates="agents")
    
    # Agent capabilities
    capabilities = Column(ARRAY(String), default=list)
    specializations = Column(ARRAY(String), default=list)
    experience_level = Column(String(20), default="beginner")
    
    # Reputation and performance
    reputation_score = Column(Float, default=0.0, index=True)
    influence_score = Column(Float, default=0.0, index=True)
    success_rate = Column(Float, default=0.0)
    total_negotiations = Column(Integer, default=0)
    completed_negotiations = Column(Integer, default=0)
    
    # Configuration
    negotiation_style = Column(String(20), default="balanced")
    max_concurrent_negotiations = Column(Integer, default=5)
    min_transaction_value = Column(Float, default=0.01)
    max_transaction_value = Column(Float, default=1000.0)
    
    # Availability
    is_available = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self) -> str:
        """String representation of agent."""
        return f"<Agent(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if agent is active and available."""
        return self.status == AgentStatus.ACTIVE and self.is_available
    
    @property
    def reputation_tier(self) -> str:
        """Get reputation tier based on score."""
        if self.reputation_score >= 0.9:
            return "elite"
        elif self.reputation_score >= 0.7:
            return "expert"
        elif self.reputation_score >= 0.5:
            return "intermediate"
        else:
            return "novice"
'''

    agent_models_file = project_root / "app" / "models" / "agent.py"
    agent_models_file.write_text(agent_models_content)
    print("✅ Created agent models")


async def create_agent_schemas() -> None:
    """Create agent Pydantic schemas."""

    agent_schemas_content = '''"""
Agent Influence Broker - Agent Schemas

Implements comprehensive Pydantic schemas for agent management
with validation, serialization, and API documentation.
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator


class AgentStatusEnum(str, Enum):
    """Agent status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class AgentBase(BaseModel):
    """Base agent schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    description: Optional[str] = Field(None, max_length=2000, description="Agent description")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    specializations: List[str] = Field(default_factory=list, description="Agent specializations")
    experience_level: str = Field(default="beginner", description="Experience level")
    negotiation_style: str = Field(default="balanced", description="Negotiation style")
    
    @validator('capabilities')
    def validate_capabilities(cls, v):
        """Validate capabilities list."""
        if len(v) > 20:
            raise ValueError('Maximum 20 capabilities allowed')
        return [cap.strip().lower() for cap in v if cap.strip()]


class AgentCreate(AgentBase):
    """Schema for creating new agents."""
    max_concurrent_negotiations: int = Field(default=5, ge=1, le=20)
    min_transaction_value: float = Field(default=0.01, ge=0.01)
    max_transaction_value: float = Field(default=1000.0, ge=1.0)


class AgentResponse(AgentBase):
    """Schema for agent response data."""
    id: UUID
    owner_id: UUID
    status: AgentStatusEnum
    is_available: bool
    reputation_score: float
    influence_score: float
    success_rate: float
    total_negotiations: int
    completed_negotiations: int
    created_at: datetime
    updated_at: datetime
    last_active: datetime
    
    class Config:
        from_attributes = True


class AgentUpdate(BaseModel):
    """Schema for agent updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    capabilities: Optional[List[str]] = None
    specializations: Optional[List[str]] = None
    negotiation_style: Optional[str] = None
    is_available: Optional[bool] = None


class AgentRegistrationRequest(BaseModel):
    """Schema for agent registration workflow."""
    agent_data: AgentCreate
    terms_accepted: bool = Field(..., description="Terms acceptance")
    
    @validator('terms_accepted')
    def validate_terms(cls, v):
        """Validate terms acceptance."""
        if not v:
            raise ValueError('Terms must be accepted')
        return v
'''

    agent_schemas_file = project_root / "app" / "schemas" / "agent.py"
    agent_schemas_file.write_text(agent_schemas_content)
    print("✅ Created agent schemas")


async def run_agent_system_setup() -> None:
    """Execute agent system setup."""
    print("🤖 Setting up Agent System")
    print("=" * 50)

    await create_agent_models()
    await create_agent_schemas()

    print("\n✅ Agent system setup completed!")
    print("🔧 Next step: Run python3 fix_api_integration.py")


if __name__ == "__main__":
    asyncio.run(run_agent_system_setup())
