"""
Agent Influence Broker - Webhook API Routes

Webhook management endpoints for real-time notifications and integrations.
"""

from typing import List

from fastapi import APIRouter, Depends, status

from app.core.logging import get_logger
from app.core.security import get_current_user_token
from app.schemas.webhook import WebhookCreateRequest, WebhookResponse
from app.services.webhook_service import webhook_engine

logger = get_logger(__name__)

router = APIRouter()


@router.post(
    "/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED
)
async def create_webhook(
    webhook_data: WebhookCreateRequest,
    current_user=Depends(get_current_user_token),
):
    """Create new webhook endpoint."""
    return await webhook_engine.create_webhook(
        webhook_data, current_user.user_id
    )


@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(current_user=Depends(get_current_user_token)):
    """List user's webhooks."""
    return await webhook_engine.list_user_webhooks(current_user.user_id)
