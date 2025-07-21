"""
Agent Influence Broker - Influence Schemas

Influence metrics Pydantic models for API validation.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class AgentInfluenceScore(BaseModel):
    """Agent influence score with breakdown."""

    agent_id: str
    overall_score: float = Field(..., ge=0.0, le=1.0)
    component_scores: Dict[str, float]
    trend_analysis: Dict[str, Any]
    calculation_date: datetime
    time_window_days: int
    confidence_level: float = Field(..., ge=0.0, le=1.0)


class InfluenceMetricsResponse(BaseModel):
    """Comprehensive influence metrics response."""

    agent_id: str
    reputation_score: float
    influence_score: float
    total_negotiations: int
    success_rate: float
    last_updated: datetime

    class Config:
        from_attributes = True


class ReputationUpdate(BaseModel):
    """Reputation update response model."""

    agent_id: str
    new_reputation_score: float
    previous_reputation_score: float
    factors_breakdown: Dict[str, float]
    calculation_date: datetime
    confidence_interval: Dict[str, float]
