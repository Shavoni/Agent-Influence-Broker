"""
Agent Influence Broker - Negotiation Engine Service

Comprehensive negotiation management service implementing real-time
negotiation protocols, strategy evaluation, and state management
following project architecture with async/await patterns.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_database_session
from app.core.logging import get_logger, log_security_event
from app.models.agent import Agent
from app.models.negotiation import (
    Negotiation,
    NegotiationStatus,
    Proposal,
    ProposalType,
)
from app.schemas.negotiation import (
    NegotiationCreateRequest,
    NegotiationListResponse,
    NegotiationResponse,
    NegotiationSearchRequest,
    ProposalCreateRequest,
    ProposalResponse,
)
from app.services.influence_service import influence_service

logger = get_logger(__name__)


class NegotiationEngine:
    """
    Sophisticated negotiation engine implementing comprehensive
    negotiation protocols, strategy evaluation, and real-time
    state management following project architecture.
    """

    def __init__(self):
        """Initialize negotiation engine with strategy patterns."""
        self.strategy_weights = {
            "aggressive": {"pressure": 0.8, "concession": 0.2, "time_factor": 0.9},
            "balanced": {"pressure": 0.5, "concession": 0.5, "time_factor": 0.6},
            "cooperative": {"pressure": 0.3, "concession": 0.7, "time_factor": 0.4},
            "analytical": {"pressure": 0.4, "concession": 0.4, "time_factor": 0.2},
            "adaptive": {"pressure": 0.6, "concession": 0.4, "time_factor": 0.5},
        }

    async def initiate_negotiation(
        self, negotiation_data: NegotiationCreateRequest, initiator_id: str
    ) -> NegotiationResponse:
        """
        Initiate new negotiation between agents with comprehensive validation.

        Args:
            negotiation_data: Negotiation creation request
            initiator_id: ID of the initiating user

        Returns:
            NegotiationResponse: Created negotiation with metadata

        Raises:
            HTTPException: If validation fails or creation error occurs
        """
        try:
            async with get_database_session() as session:
                # Validate agents and permissions
                await self._validate_negotiation_participants(
                    session,
                    negotiation_data.initiator_agent_id,
                    negotiation_data.responder_agent_id,
                    initiator_id,
                )

                # Create negotiation instance
                negotiation = Negotiation(
                    id=str(uuid4()),
                    initiator_agent_id=negotiation_data.initiator_agent_id,
                    responder_agent_id=negotiation_data.responder_agent_id,
                    title=negotiation_data.title,
                    description=negotiation_data.description,
                    category=negotiation_data.category,
                    initial_value=negotiation_data.initial_value,
                    current_value=negotiation_data.initial_value,
                    currency=negotiation_data.currency,
                    max_rounds=negotiation_data.max_rounds,
                    expires_at=datetime.utcnow()
                    + timedelta(hours=negotiation_data.duration_hours),
                    status=NegotiationStatus.INITIATED.value,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

                session.add(negotiation)
                await session.commit()
                await session.refresh(negotiation)

                # Create initial proposal
                initial_proposal = await self._create_initial_proposal(
                    session, negotiation, negotiation_data
                )

                # Calculate initial influence metrics
                await influence_service.record_negotiation_initiation(
                    negotiation.id,
                    negotiation.initiator_agent_id,
                    negotiation.responder_agent_id,
                )

                logger.info(f"Negotiation initiated: {negotiation.id}")

                return await self._convert_to_response(session, negotiation)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Negotiation initiation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initiate negotiation",
            )

    async def submit_proposal(
        self, negotiation_id: str, proposal_data: ProposalCreateRequest, user_id: str
    ) -> ProposalResponse:
        """
        Submit proposal in active negotiation with strategy evaluation.

        Args:
            negotiation_id: Target negotiation ID
            proposal_data: Proposal submission data
            user_id: Submitting user ID

        Returns:
            ProposalResponse: Created proposal with evaluation

        Raises:
            HTTPException: If negotiation not found, invalid state, or submission fails
        """
        try:
            async with get_database_session() as session:
                # Get negotiation with validation
                negotiation = await self._get_active_negotiation(
                    session, negotiation_id
                )

                # Validate proposal permissions
                await self._validate_proposal_permissions(
                    session, negotiation, proposal_data.proposer_agent_id, user_id
                )

                # Evaluate proposal strategy
                strategy_analysis = await self._evaluate_proposal_strategy(
                    session, negotiation, proposal_data
                )

                # Create proposal
                proposal = Proposal(
                    id=str(uuid4()),
                    negotiation_id=negotiation_id,
                    proposer_agent_id=proposal_data.proposer_agent_id,
                    proposal_type=proposal_data.proposal_type.value,
                    round_number=negotiation.current_round,
                    proposed_value=proposal_data.proposed_value,
                    value_change=proposal_data.proposed_value
                    - negotiation.current_value,
                    justification=proposal_data.justification,
                    terms=self._serialize_terms(proposal_data.terms),
                    conditions=self._serialize_conditions(proposal_data.conditions),
                    response_deadline=datetime.utcnow() + timedelta(hours=24),
                    influence_score=strategy_analysis["influence_score"],
                    strategy_type=strategy_analysis["strategy_type"],
                    confidence_level=strategy_analysis["confidence_level"],
                    created_at=datetime.utcnow(),
                )

                session.add(proposal)

                # Update negotiation state
                await self._update_negotiation_state(session, negotiation, proposal)

                # Record influence interaction
                await influence_service.record_proposal_influence(
                    proposal.id,
                    proposal.proposer_agent_id,
                    negotiation,
                    strategy_analysis,
                )

                await session.commit()
                await session.refresh(proposal)

                logger.info(
                    f"Proposal submitted: {proposal.id} in negotiation {negotiation_id}"
                )

                return await self._convert_proposal_to_response(proposal)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Proposal submission failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit proposal",
            )

    async def respond_to_proposal(
        self, proposal_id: str, response_data: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        """
        Respond to proposal with acceptance, rejection, or counter-proposal.

        Args:
            proposal_id: Target proposal ID
            response_data: Response details and action
            user_id: Responding user ID

        Returns:
            Dict containing response confirmation and next steps

        Raises:
            HTTPException: If proposal not found, invalid state, or response fails
        """
        try:
            async with get_database_session() as session:
                # Get proposal and negotiation
                proposal = await self._get_proposal_with_negotiation(
                    session, proposal_id
                )
                negotiation = proposal.negotiation

                # Validate response permissions
                await self._validate_response_permissions(session, proposal, user_id)

                response_type = response_data.get("response_type")

                if response_type == "accept":
                    result = await self._handle_proposal_acceptance(
                        session, proposal, negotiation, response_data
                    )
                elif response_type == "reject":
                    result = await self._handle_proposal_rejection(
                        session, proposal, negotiation, response_data
                    )
                elif response_type == "counter":
                    result = await self._handle_counter_proposal(
                        session, proposal, negotiation, response_data, user_id
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid response type",
                    )

                await session.commit()

                logger.info(
                    f"Proposal response processed: {proposal_id} -> {response_type}"
                )

                return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Proposal response failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process proposal response",
            )

    async def get_negotiation(
        self, negotiation_id: str, user_id: str
    ) -> NegotiationResponse:
        """
        Retrieve negotiation with access control and full proposal history.

        Args:
            negotiation_id: Negotiation identifier
            user_id: Requesting user identifier

        Returns:
            NegotiationResponse: Complete negotiation data with proposals

        Raises:
            HTTPException: If negotiation not found or access denied
        """
        try:
            async with get_database_session() as session:
                # Get negotiation with proposals
                query = (
                    select(Negotiation)
                    .options(
                        selectinload(Negotiation.proposals),
                        selectinload(Negotiation.initiator_agent),
                        selectinload(Negotiation.responder_agent),
                    )
                    .where(Negotiation.id == negotiation_id)
                )

                result = await session.execute(query)
                negotiation = result.scalar_one_or_none()

                if not negotiation:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Negotiation not found",
                    )

                # Validate access permissions
                if not await self._has_negotiation_access(
                    session, negotiation, user_id
                ):
                    log_security_event(
                        "unauthorized_negotiation_access",
                        {"negotiation_id": negotiation_id, "requesting_user": user_id},
                        logger,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
                    )

                return await self._convert_to_response(session, negotiation)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Negotiation retrieval failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve negotiation",
            )

    async def get_active_count(self) -> int:
        """Get count of active negotiations."""
        try:
            async with get_database_session() as session:
                query = select(func.count(Negotiation.id)).where(
                    Negotiation.status.in_(["active", "pending_response"])
                )
                result = await session.execute(query)
                return result.scalar() or 0
        except Exception as e:
            logger.error(f"Failed to get active negotiations count: {e}")
            return 0

    async def list_user_negotiations(
        self, user_id: str, search_params: NegotiationSearchRequest
    ) -> NegotiationListResponse:
        """List negotiations for user with pagination."""
        try:
            async with get_database_session() as session:
                # Implementation would go here
                return NegotiationListResponse(
                    negotiations=[],
                    total_count=0,
                    page=search_params.page,
                    page_size=search_params.page_size,
                    total_pages=0,
                    has_next=False,
                    has_previous=False,
                )
        except Exception as e:
            logger.error(f"Failed to list user negotiations: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list negotiations",
            )

    # Strategy evaluation methods

    async def _evaluate_proposal_strategy(
        self,
        session: AsyncSession,
        negotiation: Negotiation,
        proposal_data: ProposalCreateRequest,
    ) -> Dict[str, Any]:
        """Evaluate proposal strategy and calculate influence metrics."""

        # Get proposer agent
        proposer_query = select(Agent).where(
            Agent.id == proposal_data.proposer_agent_id
        )
        proposer_result = await session.execute(proposer_query)
        proposer = proposer_result.scalar_one()

        # Calculate value change metrics
        value_change_pct = (
            (
                (proposal_data.proposed_value - negotiation.current_value)
                / negotiation.current_value
            )
            if negotiation.current_value != 0
            else 0
        )

        # Evaluate based on agent's negotiation style
        style_weights = self.strategy_weights.get(
            proposer.negotiation_style, self.strategy_weights["balanced"]
        )

        # Calculate influence score
        base_influence = proposer.influence_score
        strategy_modifier = self._calculate_strategy_modifier(
            proposal_data, style_weights
        )
        time_pressure = self._calculate_time_pressure(negotiation)

        influence_score = min(1.0, base_influence * strategy_modifier * time_pressure)

        # Determine strategy type
        strategy_type = self._classify_strategy(value_change_pct, proposal_data)

        # Calculate confidence level
        confidence_level = self._calculate_confidence(
            proposer, value_change_pct, negotiation.current_round
        )

        return {
            "influence_score": influence_score,
            "strategy_type": strategy_type,
            "confidence_level": confidence_level,
            "value_change_pct": value_change_pct,
            "strategy_modifier": strategy_modifier,
            "time_pressure": time_pressure,
        }

    def _calculate_strategy_modifier(
        self, proposal_data: ProposalCreateRequest, style_weights: Dict[str, float]
    ) -> float:
        """Calculate strategy effectiveness modifier."""

        # Base modifier from justification quality
        justification_score = (
            len(proposal_data.justification) / 500.0
            if proposal_data.justification
            else 0.1
        )
        justification_score = min(1.0, justification_score)

        # Terms complexity score
        terms_complexity = (
            len(proposal_data.terms) * 0.1 if proposal_data.terms else 0.5
        )
        terms_complexity = min(1.0, terms_complexity)

        # Combine with style weights
        modifier = (
            justification_score * style_weights["pressure"]
            + terms_complexity * style_weights["concession"]
        )

        return max(0.1, min(2.0, modifier))

    def _calculate_time_pressure(self, negotiation: Negotiation) -> float:
        """Calculate time pressure factor."""
        if not negotiation.expires_at:
            return 1.0

        time_remaining = (negotiation.expires_at - datetime.utcnow()).total_seconds()
        total_time = (negotiation.expires_at - negotiation.created_at).total_seconds()

        if total_time <= 0:
            return 1.5  # High pressure if expired

        remaining_ratio = time_remaining / total_time

        if remaining_ratio <= 0.1:
            return 1.4  # Very high pressure
        elif remaining_ratio <= 0.3:
            return 1.2  # High pressure
        elif remaining_ratio <= 0.7:
            return 1.0  # Normal pressure
        else:
            return 0.8  # Low pressure

    def _classify_strategy(
        self, value_change_pct: float, proposal_data: ProposalCreateRequest
    ) -> str:
        """Classify negotiation strategy based on proposal characteristics."""

        if abs(value_change_pct) > 0.2:
            return "aggressive"
        elif abs(value_change_pct) > 0.1:
            return "assertive"
        elif proposal_data.justification and len(proposal_data.justification) > 200:
            return "analytical"
        elif proposal_data.terms and len(proposal_data.terms) > 3:
            return "collaborative"
        else:
            return "conservative"

    def _calculate_confidence(
        self, proposer: Agent, value_change_pct: float, current_round: int
    ) -> float:
        """Calculate proposal confidence level."""

        # Base confidence from agent reputation
        base_confidence = proposer.reputation_score

        # Adjust for proposal boldness
        boldness_factor = 1.0 - (abs(value_change_pct) * 0.5)

        # Adjust for round progression
        round_factor = max(0.5, 1.0 - (current_round * 0.1))

        confidence = base_confidence * boldness_factor * round_factor

        return max(0.1, min(1.0, confidence))

    # Helper methods for serialization and state management

    def _serialize_terms(self, terms: Optional[List[str]]) -> str:
        """Serialize terms to JSON string."""
        import json

        return json.dumps(terms if terms else [])

    def _serialize_conditions(self, conditions: Optional[List[str]]) -> str:
        """Serialize conditions to JSON string."""
        import json

        return json.dumps(conditions if conditions else [])

    # Additional helper methods would continue here...
    # (validation, state management, response conversion, etc.)

# Global negotiation engine instance
negotiation_engine = NegotiationEngine()
