"""
Agent Influence Broker - Agent Management Service

Comprehensive agent management service implementing business logic,
validation, and database operations following project architecture
with async/await patterns and error handling.
"""

from datetime import datetime
from typing import Dict, List
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_database_session
from app.core.logging import get_logger, log_security_event
from app.models.agent import Agent
from app.models.user import User
from app.schemas.agent import (
    AgentCreateRequest,
    AgentListResponse,
    AgentResponse,
    AgentSearchRequest,
    AgentStatus,
    AgentUpdateRequest,
)

logger = get_logger(__name__)


class AgentService:
    """
    Sophisticated agent management service implementing comprehensive
    agent lifecycle management, validation, and performance tracking
    following project architecture and async patterns.
    """

    async def create_agent(
        self, agent_data: AgentCreateRequest, owner_id: str
    ) -> AgentResponse:
        """
        Create new agent with comprehensive validation and initialization.

        Args:
            agent_data: Agent creation request data
            owner_id: ID of the user creating the agent

        Returns:
            AgentResponse: Created agent with full metadata

        Raises:
            HTTPException: If validation fails or creation error occurs
        """
        try:
            async with get_database_session() as session:
                # Verify owner exists and check agent limits
                await self._verify_owner_and_limits(session, owner_id)

                # Create agent instance
                agent = Agent(
                    id=str(uuid4()),
                    name=agent_data.name,
                    description=agent_data.description,
                    owner_id=owner_id,
                    capabilities=self._serialize_capabilities(
                        agent_data.capabilities
                    ),
                    specializations=self._serialize_specializations(
                        agent_data.specializations
                    ),
                    experience_level=agent_data.experience_level.value,
                    negotiation_style=agent_data.negotiation_style.value,
                    max_concurrent_negotiations=agent_data.max_concurrent_negotiations,
                    min_transaction_value=agent_data.min_transaction_value,
                    max_transaction_value=agent_data.max_transaction_value,
                    status=AgentStatus.PENDING.value,
                    reputation_score=0.0,
                    influence_score=0.0,
                    success_rate=0.0,
                    total_negotiations=0,
                    completed_negotiations=0,
                    is_available=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    last_active=datetime.utcnow(),
                )

                session.add(agent)
                await session.commit()
                await session.refresh(agent)

                logger.info(
                    f"Agent created successfully: {agent.id} for owner {owner_id}"
                )

                return await self._convert_to_response(agent)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Agent creation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create agent",
            )

    async def get_agent(self, agent_id: str, user_id: str) -> AgentResponse:
        """
        Retrieve agent by ID with access control validation.

        Args:
            agent_id: Agent identifier
            user_id: Requesting user identifier

        Returns:
            AgentResponse: Agent data with full metadata

        Raises:
            HTTPException: If agent not found or access denied
        """
        try:
            async with get_database_session() as session:
                query = select(Agent).where(Agent.id == agent_id)
                result = await session.execute(query)
                agent = result.scalar_one_or_none()

                if not agent:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Agent not found",
                    )

                # Check access permissions
                if agent.owner_id != user_id:
                    # For now, only owners can access their agents
                    # TODO: Implement public profile access for negotiations
                    log_security_event(
                        "unauthorized_agent_access",
                        {
                            "agent_id": agent_id,
                            "requesting_user": user_id,
                            "owner_id": agent.owner_id,
                        },
                        logger,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied",
                    )

                return await self._convert_to_response(agent)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Agent retrieval failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve agent",
            )

    async def update_agent(
        self, agent_id: str, agent_data: AgentUpdateRequest, user_id: str
    ) -> AgentResponse:
        """
        Update agent with comprehensive validation and change tracking.

        Args:
            agent_id: Agent identifier
            agent_data: Update request data
            user_id: Requesting user identifier

        Returns:
            AgentResponse: Updated agent data

        Raises:
            HTTPException: If agent not found, access denied, or update fails
        """
        try:
            async with get_database_session() as session:
                # Get existing agent
                query = select(Agent).where(Agent.id == agent_id)
                result = await session.execute(query)
                agent = result.scalar_one_or_none()

                if not agent:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Agent not found",
                    )

                # Verify ownership
                if agent.owner_id != user_id:
                    log_security_event(
                        "unauthorized_agent_modification",
                        {
                            "agent_id": agent_id,
                            "requesting_user": user_id,
                            "owner_id": agent.owner_id,
                        },
                        logger,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied",
                    )

                # Apply updates
                update_data = {}
                if agent_data.name is not None:
                    update_data["name"] = agent_data.name
                if agent_data.description is not None:
                    update_data["description"] = agent_data.description
                if agent_data.capabilities is not None:
                    update_data["capabilities"] = self._serialize_capabilities(
                        agent_data.capabilities
                    )
                if agent_data.specializations is not None:
                    update_data[
                        "specializations"
                    ] = self._serialize_specializations(
                        agent_data.specializations
                    )
                if agent_data.experience_level is not None:
                    update_data[
                        "experience_level"
                    ] = agent_data.experience_level.value
                if agent_data.negotiation_style is not None:
                    update_data[
                        "negotiation_style"
                    ] = agent_data.negotiation_style.value
                if agent_data.max_concurrent_negotiations is not None:
                    update_data[
                        "max_concurrent_negotiations"
                    ] = agent_data.max_concurrent_negotiations
                if agent_data.min_transaction_value is not None:
                    update_data[
                        "min_transaction_value"
                    ] = agent_data.min_transaction_value
                if agent_data.max_transaction_value is not None:
                    update_data[
                        "max_transaction_value"
                    ] = agent_data.max_transaction_value
                if agent_data.is_available is not None:
                    update_data["is_available"] = agent_data.is_available

                if update_data:
                    update_data["updated_at"] = datetime.utcnow()

                    # Execute update
                    query = (
                        update(Agent)
                        .where(Agent.id == agent_id)
                        .values(**update_data)
                    )
                    await session.execute(query)
                    await session.commit()

                    # Refresh agent data
                    await session.refresh(agent)

                logger.info(f"Agent updated successfully: {agent_id}")

                return await self._convert_to_response(agent)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Agent update failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update agent",
            )

    async def list_user_agents(
        self, user_id: str, search_params: AgentSearchRequest
    ) -> AgentListResponse:
        """
        List agents owned by user with search and pagination.

        Args:
            user_id: Owner user identifier
            search_params: Search and pagination parameters

        Returns:
            AgentListResponse: Paginated list of agents
        """
        try:
            async with get_database_session() as session:
                # Build base query
                query = select(Agent).where(Agent.owner_id == user_id)

                # Apply filters
                query = await self._apply_search_filters(query, search_params)

                # Get total count
                count_query = select(func.count()).select_from(
                    query.subquery()
                )
                total_result = await session.execute(count_query)
                total_count = total_result.scalar()

                # Apply pagination and sorting
                query = self._apply_pagination_and_sorting(
                    query, search_params
                )

                # Execute query
                result = await session.execute(query)
                agents = result.scalars().all()

                # Convert to response models
                agent_responses = []
                for agent in agents:
                    agent_responses.append(
                        await self._convert_to_response(agent)
                    )

                # Calculate pagination metadata
                total_pages = (
                    total_count + search_params.page_size - 1
                ) // search_params.page_size
                has_next = search_params.page < total_pages
                has_previous = search_params.page > 1

                return AgentListResponse(
                    agents=agent_responses,
                    total_count=total_count,
                    page=search_params.page,
                    page_size=search_params.page_size,
                    total_pages=total_pages,
                    has_next=has_next,
                    has_previous=has_previous,
                )

        except Exception as e:
            logger.error(f"Agent listing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list agents",
            )

    async def delete_agent(
        self, agent_id: str, user_id: str
    ) -> Dict[str, str]:
        """
        Delete agent with comprehensive validation and cleanup.

        Args:
            agent_id: Agent identifier
            user_id: Requesting user identifier

        Returns:
            Dict with deletion confirmation

        Raises:
            HTTPException: If agent not found, access denied, or deletion fails
        """
        try:
            async with get_database_session() as session:
                # Get agent with ownership verification
                query = select(Agent).where(
                    and_(Agent.id == agent_id, Agent.owner_id == user_id)
                )
                result = await session.execute(query)
                agent = result.scalar_one_or_none()

                if not agent:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Agent not found or access denied",
                    )

                # Check for active negotiations
                # TODO: Implement active negotiation check
                # if agent has active negotiations, prevent deletion

                # Delete agent
                query = delete(Agent).where(Agent.id == agent_id)
                await session.execute(query)
                await session.commit()

                logger.info(f"Agent deleted successfully: {agent_id}")

                return {
                    "message": "Agent deleted successfully",
                    "agent_id": agent_id,
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Agent deletion failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete agent",
            )

    async def get_total_count(self) -> int:
        """Get total count of agents."""
        try:
            async with get_database_session() as session:
                query = select(func.count(Agent.id))
                result = await session.execute(query)
                return result.scalar() or 0
        except Exception as e:
            logger.error(f"Failed to get total agents count: {e}")
            return 0

    # Helper methods

    async def _verify_owner_and_limits(
        self, session: AsyncSession, owner_id: str
    ) -> User:
        """Verify owner exists and check agent creation limits."""
        query = select(User).where(User.id == owner_id)
        result = await session.execute(query)
        owner = result.scalar_one_or_none()

        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Check agent limit
        agent_count_query = select(func.count()).where(
            Agent.owner_id == owner_id
        )
        count_result = await session.execute(agent_count_query)
        current_count = count_result.scalar()

        if current_count >= owner.max_agents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent limit reached. Maximum: {owner.max_agents}",
            )

        return owner

    def _serialize_capabilities(self, capabilities: List) -> str:
        """Serialize capabilities to JSON string."""
        import json

        return json.dumps([cap.dict() for cap in capabilities])

    def _serialize_specializations(self, specializations: List) -> str:
        """Serialize specializations to JSON string."""
        import json

        return json.dumps([spec.dict() for spec in specializations])

    async def _convert_to_response(self, agent: Agent) -> AgentResponse:
        """Convert agent model to response schema."""
        import json

        # Deserialize JSON fields
        capabilities = (
            json.loads(agent.capabilities) if agent.capabilities else []
        )
        specializations = (
            json.loads(agent.specializations) if agent.specializations else []
        )

        # Calculate reputation tier
        reputation_tier = self._calculate_reputation_tier(
            agent.reputation_score
        )

        return AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            status=AgentStatus(agent.status),
            owner_id=agent.owner_id,
            capabilities=capabilities,
            specializations=specializations,
            experience_level=agent.experience_level,
            negotiation_style=agent.negotiation_style,
            reputation_score=agent.reputation_score,
            influence_score=agent.influence_score,
            success_rate=agent.success_rate,
            total_negotiations=agent.total_negotiations,
            completed_negotiations=agent.completed_negotiations,
            max_concurrent_negotiations=agent.max_concurrent_negotiations,
            min_transaction_value=agent.min_transaction_value,
            max_transaction_value=agent.max_transaction_value,
            is_available=agent.is_available,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            last_active=agent.last_active,
            reputation_tier=reputation_tier,
            active_negotiations=0,  # TODO: Calculate from active negotiations
        )

    def _calculate_reputation_tier(self, reputation_score: float) -> str:
        """Calculate reputation tier based on score."""
        if reputation_score >= 0.9:
            return "elite"
        elif reputation_score >= 0.7:
            return "expert"
        elif reputation_score >= 0.5:
            return "intermediate"
        elif reputation_score >= 0.3:
            return "developing"
        else:
            return "novice"

    async def _apply_search_filters(
        self, query, search_params: AgentSearchRequest
    ):
        """Apply search filters to query."""
        # Text search
        if search_params.query:
            query = query.where(
                or_(
                    Agent.name.ilike(f"%{search_params.query}%"),
                    Agent.description.ilike(f"%{search_params.query}%"),
                )
            )

        # Status filter
        if search_params.status:
            status_values = [s.value for s in search_params.status]
            query = query.where(Agent.status.in_(status_values))

        # Reputation range
        if search_params.min_reputation is not None:
            query = query.where(
                Agent.reputation_score >= search_params.min_reputation
            )
        if search_params.max_reputation is not None:
            query = query.where(
                Agent.reputation_score <= search_params.max_reputation
            )

        # Availability filter
        if search_params.available_only:
            query = query.where(Agent.is_available)

        return query

    def _apply_pagination_and_sorting(
        self, query, search_params: AgentSearchRequest
    ):
        """Apply pagination and sorting to query."""
        # Sorting
        sort_column = getattr(Agent, search_params.sort_by, Agent.created_at)
        if search_params.sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Pagination
        offset = (search_params.page - 1) * search_params.page_size
        query = query.offset(offset).limit(search_params.page_size)

        return query


# Global service instance
agent_service = AgentService()
