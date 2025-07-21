"""
Agent Service - Business logic for agent operations
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import get_password_hash
from ..models.agents import Agent
from ..schemas.agents import (
    AgentCreate,
    AgentListResponse,
    AgentSearchFilters,
    AgentStats,
    AgentSummary,
    AgentUpdate,
)


class AgentService:
    """Service class for agent operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_agent(
        self, agent_data: AgentCreate, owner_id: str
    ) -> Agent:
        """Create a new agent"""
        # Hash API key if provided
        api_key_hash = None
        if agent_data.api_key:
            api_key_hash = get_password_hash(agent_data.api_key)

        agent = Agent(
            name=agent_data.name,
            description=agent_data.description,
            agent_type=agent_data.agent_type,
            owner_id=owner_id,
            capabilities=[cap.dict() for cap in agent_data.capabilities],
            metadata=agent_data.metadata,
            api_endpoint=agent_data.api_endpoint,
            webhook_url=agent_data.webhook_url,
            api_key_hash=api_key_hash,
            last_active=datetime.utcnow(),
        )

        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def get_agent_by_id(self, agent_id: uuid.UUID) -> Optional[Agent]:
        """Get agent by ID"""
        result = await self.db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        return result.scalar_one_or_none()

    async def get_agents_by_owner(self, owner_id: str) -> List[AgentSummary]:
        """Get all agents owned by a user"""
        result = await self.db.execute(
            select(Agent).where(Agent.owner_id == owner_id)
        )
        agents = result.scalars().all()
        return [AgentSummary.from_orm(agent) for agent in agents]

    async def list_agents(
        self,
        page: int = 1,
        size: int = 20,
        filters: Optional[AgentSearchFilters] = None,
    ) -> AgentListResponse:
        """List agents with pagination and filtering"""
        query = select(Agent)

        # Apply filters
        if filters:
            if filters.agent_type:
                query = query.where(Agent.agent_type == filters.agent_type)
            if filters.is_active is not None:
                query = query.where(Agent.is_active == filters.is_active)
            if filters.is_verified is not None:
                query = query.where(Agent.is_verified == filters.is_verified)
            if filters.min_reputation is not None:
                query = query.where(
                    Agent.reputation_score >= filters.min_reputation
                )
            if filters.max_reputation is not None:
                query = query.where(
                    Agent.reputation_score <= filters.max_reputation
                )

        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar()

        # Apply pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await self.db.execute(query)
        agents = result.scalars().all()

        return AgentListResponse(
            agents=[AgentSummary.from_orm(agent) for agent in agents],
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size,
        )

    async def update_agent(
        self, agent_id: uuid.UUID, agent_data: AgentUpdate
    ) -> Agent:
        """Update an agent"""
        update_data = agent_data.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        await self.db.execute(
            update(Agent).where(Agent.id == agent_id).values(**update_data)
        )
        await self.db.commit()

        # Return updated agent
        return await self.get_agent_by_id(agent_id)

    async def deactivate_agent(self, agent_id: uuid.UUID) -> None:
        """Deactivate an agent (soft delete)"""
        await self.db.execute(
            update(Agent)
            .where(Agent.id == agent_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        await self.db.commit()

    async def activate_agent(self, agent_id: uuid.UUID) -> None:
        """Activate an agent"""
        await self.db.execute(
            update(Agent)
            .where(Agent.id == agent_id)
            .values(is_active=True, updated_at=datetime.utcnow())
        )
        await self.db.commit()

    async def verify_agent(self, agent_id: uuid.UUID) -> None:
        """Verify an agent"""
        await self.db.execute(
            update(Agent)
            .where(Agent.id == agent_id)
            .values(is_verified=True, updated_at=datetime.utcnow())
        )
        await self.db.commit()

    async def get_agent_stats(self, agent_id: uuid.UUID) -> AgentStats:
        """Get agent statistics"""
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            raise ValueError("Agent not found")

        # For now, return basic stats from the agent model
        # In a real implementation, you'd query related tables
        return AgentStats(
            total_negotiations=agent.total_negotiations,
            successful_negotiations=agent.successful_negotiations,
            success_rate=agent.success_rate,
            average_satisfaction=0.85,  # Mock data
            reputation_score=agent.reputation_score,
            influence_score=agent.influence_score,
            last_30_days_activity=5,  # Mock data
            total_earnings=1250.50,  # Mock data
            total_spent=890.25,  # Mock data
        )
