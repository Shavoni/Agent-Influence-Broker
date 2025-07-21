"""
Agent Influence Broker - Webhook Schemas

Webhook-related Pydantic models for API validation.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class WebhookCreateRequest(BaseModel):
    """Request model for creating webhooks."""

    url: HttpUrl
    events: List[str] = Field(..., min_items=1)
    is_active: bool = Field(default=True)
    description: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None
    timeout_seconds: Optional[int] = Field(default=30, ge=5, le=60)
    max_retries: Optional[int] = Field(default=5, ge=0, le=10)


class WebhookResponse(BaseModel):
    """Response model for webhook data."""

    id: str
    url: str
    events: List[str]
    is_active: bool
    description: Optional[str]

    class Config:
        from_attributes = True
