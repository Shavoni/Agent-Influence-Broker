"""
Negotiation database models
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..core.database import Base


class NegotiationStatus(enum.Enum):
    """Negotiation status enumeration"""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class NegotiationPhase(enum.Enum):
    """Negotiation phase enumeration"""

    INITIALIZATION = "initialization"
    PROPOSAL = "proposal"
    COUNTER_PROPOSAL = "counter_proposal"
    BARGAINING = "bargaining"
    AGREEMENT = "agreement"
    FINALIZATION = "finalization"


class Negotiation(Base):
    """Negotiation model for agent-to-agent negotiations"""

    __tablename__ = "negotiations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)

    # Participants
    initiator_agent_id = Column(
        UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False
    )
    responder_agent_id = Column(
        UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False
    )

    # Negotiation details
    # "trade", "service", "collaboration"
    negotiation_type = Column(String(100), nullable=False)
    status = Column(Enum(NegotiationStatus), default=NegotiationStatus.PENDING)
    current_phase = Column(
        Enum(NegotiationPhase), default=NegotiationPhase.INITIALIZATION
    )

    # Terms and conditions
    initial_proposal = Column(JSON)
    current_terms = Column(JSON)
    final_agreement = Column(JSON)

    # Negotiation parameters
    max_rounds = Column(Integer, default=10)
    current_round = Column(Integer, default=0)
    timeout_minutes = Column(Integer, default=60)

    # Outcome and metrics
    outcome = Column(String(100))  # "agreement", "disagreement", "timeout"
    influence_changes = Column(JSON)  # Track influence score changes
    satisfaction_scores = Column(JSON)  # Participant satisfaction

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    initiator = relationship("Agent", foreign_keys=[initiator_agent_id])
    responder = relationship("Agent", foreign_keys=[responder_agent_id])
    messages = relationship("NegotiationMessage", back_populates="negotiation")

    def __repr__(self):
        return f"<Negotiation(id={self.id}, status={self.status.value}, phase={self.current_phase.value})>"

    def is_active(self) -> bool:
        """Check if negotiation is currently active"""
        return self.status == NegotiationStatus.ACTIVE

    def is_expired(self) -> bool:
        """Check if negotiation has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    def can_proceed_to_next_round(self) -> bool:
        """Check if negotiation can proceed to next round"""
        return (
            self.is_active()
            and not self.is_expired()
            and self.current_round < self.max_rounds
        )


class NegotiationMessage(Base):
    """Messages exchanged during negotiations"""

    __tablename__ = "negotiation_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    negotiation_id = Column(
        UUID(as_uuid=True), ForeignKey("negotiations.id"), nullable=False
    )
    sender_agent_id = Column(
        UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False
    )

    # Message content
    # "proposal", "counter", "acceptance", "rejection"
    message_type = Column(String(50), nullable=False)
    content = Column(JSON, nullable=False)
    proposal_terms = Column(JSON)

    # Message metadata
    round_number = Column(Integer, nullable=False)
    phase = Column(Enum(NegotiationPhase), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    negotiation = relationship("Negotiation", back_populates="messages")
    sender = relationship("Agent")

    def __repr__(self):
        return f"<NegotiationMessage(id={self.id}, type={self.message_type}, round={self.round_number})>"
