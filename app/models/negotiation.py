"""
Agent Influence Broker - Negotiation Database Models

Comprehensive negotiation models implementing the negotiation lifecycle,
proposals, and state management following project architecture
with SQLAlchemy async patterns.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field
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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.core.database import Base

Base = declarative_base()


class NegotiationStatus(str, Enum):
    """Negotiation status enumeration for state management."""

    INITIATED = "initiated"
    ACTIVE = "active"
    PENDING_RESPONSE = "pending_response"
    COUNTER_PROPOSED = "counter_proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    COMPLETED = "completed"


class ProposalType(str, Enum):
    """Proposal type enumeration for negotiation actions."""

    INITIAL_OFFER = "initial_offer"
    COUNTER_OFFER = "counter_offer"
    FINAL_OFFER = "final_offer"
    ACCEPTANCE = "acceptance"
    REJECTION = "rejection"
    WITHDRAWAL = "withdrawal"


class Negotiation(Base):
    """
    Negotiation model implementing comprehensive negotiation lifecycle
    with state management, participant tracking, and value exchange.
    """

    __tablename__ = "negotiations"

    # Primary identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    # Participants
    initiator_agent_id = Column(
        String(36), ForeignKey("agents.id"), nullable=False
    )
    responder_agent_id = Column(
        String(36), ForeignKey("agents.id"), nullable=False
    )

    # Negotiation metadata
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))

    # State management
    status = Column(
        String(50), default=NegotiationStatus.INITIATED.value, nullable=False
    )
    current_round = Column(Integer, default=1)
    max_rounds = Column(Integer, default=10)

    # Value and terms
    initial_value = Column(Float, nullable=False)
    current_value = Column(Float)
    final_value = Column(Float)
    currency = Column(String(10), default="USD")

    # Timing constraints
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    expires_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Performance metrics
    total_proposals = Column(Integer, default=0)
    influence_factor = Column(Float, default=0.0)
    complexity_score = Column(Float, default=0.0)

    # Relationships
    proposals = relationship(
        "Proposal", back_populates="negotiation", cascade="all, delete-orphan"
    )
    initiator_agent = relationship("Agent", foreign_keys=[initiator_agent_id])
    responder_agent = relationship("Agent", foreign_keys=[responder_agent_id])


class Proposal(Base):
    """
    Proposal model implementing individual negotiation proposals
    with comprehensive tracking and validation.
    """

    __tablename__ = "proposals"

    # Primary identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    negotiation_id = Column(
        String(36), ForeignKey("negotiations.id"), nullable=False
    )

    # Proposal details
    proposer_agent_id = Column(
        String(36), ForeignKey("agents.id"), nullable=False
    )
    proposal_type = Column(String(50), nullable=False)
    round_number = Column(Integer, nullable=False)

    # Value proposition
    proposed_value = Column(Float, nullable=False)
    value_change = Column(Float)
    justification = Column(Text)

    # Terms and conditions
    terms = Column(Text)  # JSON serialized terms
    conditions = Column(Text)  # JSON serialized conditions

    # Response tracking
    response_required = Column(Boolean, default=True)
    responded_at = Column(DateTime)
    response_deadline = Column(DateTime)

    # Influence and strategy
    influence_score = Column(Float, default=0.0)
    strategy_type = Column(String(50))
    confidence_level = Column(Float, default=0.5)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    negotiation = relationship("Negotiation", back_populates="proposals")
    proposer_agent = relationship("Agent", foreign_keys=[proposer_agent_id])


class InfluenceRecord(Base):
    """
    Influence record model tracking agent influence interactions
    and metrics calculation for reputation scoring.
    """

    __tablename__ = "influence_records"

    # Primary identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))

    # Participants
    influencer_agent_id = Column(
        String(36), ForeignKey("agents.id"), nullable=False
    )
    influenced_agent_id = Column(
        String(36), ForeignKey("agents.id"), nullable=False
    )
    negotiation_id = Column(
        String(36), ForeignKey("negotiations.id"), nullable=False
    )

    # Influence metrics
    influence_type = Column(
        String(50), nullable=False
    )  # persuasion, authority, expertise, etc.
    influence_strength = Column(Float, nullable=False)  # 0.0 to 1.0
    influence_direction = Column(String(20))  # positive, negative, neutral

    # Context
    context = Column(Text)  # JSON serialized context data
    outcome = Column(String(50))  # successful, partial, failed

    # Measurement
    baseline_value = Column(Float)
    influenced_value = Column(Float)
    value_shift = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    influencer_agent = relationship(
        "Agent", foreign_keys=[influencer_agent_id]
    )
    influenced_agent = relationship(
        "Agent", foreign_keys=[influenced_agent_id]
    )
    negotiation = relationship("Negotiation", foreign_keys=[negotiation_id])


class Transaction(Base):
    """
    Transaction model implementing secure value exchange
    between agents with comprehensive audit trail.
    """

    __tablename__ = "transactions"

    # Primary identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    negotiation_id = Column(
        String(36), ForeignKey("negotiations.id"), nullable=False
    )

    # Transaction parties
    sender_agent_id = Column(
        String(36), ForeignKey("agents.id"), nullable=False
    )
    receiver_agent_id = Column(
        String(36), ForeignKey("agents.id"), nullable=False
    )

    # Transaction details
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    transaction_type = Column(String(50), default="negotiation_settlement")

    # Status and processing
    status = Column(String(50), default="pending")
    processed_at = Column(DateTime)
    confirmed_at = Column(DateTime)

    # Fees and charges
    platform_fee = Column(Float, default=0.0)
    processing_fee = Column(Float, default=0.0)
    net_amount = Column(Float)

    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    reference_id = Column(String(100))  # External transaction reference

    # Relationships
    negotiation = relationship("Negotiation", foreign_keys=[negotiation_id])
    sender_agent = relationship("Agent", foreign_keys=[sender_agent_id])
    receiver_agent = relationship("Agent", foreign_keys=[receiver_agent_id])


# Pydantic Models for API Schemas

class NegotiationTerms(BaseModel):
    """Terms and conditions for negotiations."""
    conditions: Dict[str, str] = Field(default_factory=dict)
    requirements: List[str] = Field(default_factory=list)
    constraints: Dict[str, str] = Field(default_factory=dict)


class NegotiationCreate(BaseModel):
    """Schema for creating new negotiations."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = None
    responder_agent_id: str = Field(..., min_length=1)
    initial_value: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=10)
    max_rounds: int = Field(default=10, ge=1, le=50)
    expires_at: Optional[datetime] = None
    terms: Optional[NegotiationTerms] = None


class NegotiationUpdate(BaseModel):
    """Schema for updating negotiations."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[NegotiationStatus] = None
    current_value: Optional[float] = Field(None, gt=0)
    max_rounds: Optional[int] = Field(None, ge=1, le=50)
    expires_at: Optional[datetime] = None


class NegotiationResponse(BaseModel):
    """Schema for negotiation responses."""
    id: str
    title: str
    description: Optional[str]
    category: Optional[str]
    status: NegotiationStatus
    initiator_agent_id: str
    responder_agent_id: str
    current_round: int
    max_rounds: int
    initial_value: float
    current_value: Optional[float]
    final_value: Optional[float]
    currency: str
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    completed_at: Optional[datetime]
    total_proposals: int
    influence_factor: float
    complexity_score: float

    class Config:
        from_attributes = True


class ProposalCreate(BaseModel):
    """Schema for creating proposals."""
    proposal_type: ProposalType
    proposed_value: float = Field(..., gt=0)
    justification: Optional[str] = None
    terms: Optional[Dict[str, str]] = Field(default_factory=dict)
    conditions: Optional[Dict[str, str]] = Field(default_factory=dict)
    response_deadline: Optional[datetime] = None
    strategy_type: Optional[str] = None
    confidence_level: float = Field(default=0.5, ge=0.0, le=1.0)


class ProposalResponse(BaseModel):
    """Schema for proposal responses."""
    id: str
    negotiation_id: str
    proposer_agent_id: str
    proposal_type: ProposalType
    round_number: int
    proposed_value: float
    value_change: Optional[float]
    justification: Optional[str]
    terms: Optional[str]
    conditions: Optional[str]
    response_required: bool
    responded_at: Optional[datetime]
    response_deadline: Optional[datetime]
    influence_score: float
    strategy_type: Optional[str]
    confidence_level: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
