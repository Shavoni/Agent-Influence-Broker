"""
Agent database models
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID

from ..core.database import Base


class Agent(Base):
    """Agent model for AI agents in the system"""

    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    # "trading", "negotiation", "influence", etc.
    agent_type = Column(String(100), nullable=False)

    # Owner information
    owner_id = Column(String(255), nullable=False, index=True)

    # Agent capabilities and metadata
    capabilities = Column(JSON)  # List of capabilities
    metadata = Column(JSON)  # Additional metadata

    # Reputation and scoring
    reputation_score = Column(Float, default=0.0)
    influence_score = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    total_negotiations = Column(Integer, default=0)
    successful_negotiations = Column(Integer, default=0)

    # Agent status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # API and webhook configuration
    api_endpoint = Column(String(500))
    webhook_url = Column(String(500))
    api_key_hash = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_active = Column(DateTime)

    def __repr__(self):
        return (
            f"<Agent(id={self.id}, name={self.name}, type={self.agent_type})>"
        )

    def update_reputation(self, negotiation_successful: bool):
        """Update agent reputation based on negotiation outcome"""
        self.total_negotiations += 1
        if negotiation_successful:
            self.successful_negotiations += 1

        self.success_rate = (
            self.successful_negotiations / self.total_negotiations
        )

        # Simple reputation calculation (can be made more sophisticated)
        self.reputation_score = self.success_rate * 100
        self.updated_at = datetime.utcnow()

    def calculate_influence_score(self) -> float:
        """Calculate influence score based on various factors"""
        # Base score from reputation
        base_score = self.reputation_score

        # Bonus for activity
        activity_bonus = min(self.total_negotiations * 0.1, 10)

        # Bonus for verification
        verification_bonus = 5 if self.is_verified else 0

        influence_score = base_score + activity_bonus + verification_bonus
        return min(influence_score, 100)  # Cap at 100
