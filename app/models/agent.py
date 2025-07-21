"""
Agent Influence Broker - Agent Models

Implements agent database models with capabilities, reputation,
and performance tracking following Supabase RLS patterns.
"""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID as SQLAlchemyUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
    owner_id = Column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
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
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
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
