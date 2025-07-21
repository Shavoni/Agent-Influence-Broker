"""
Webhook API routes
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db_session
from ..core.security import require_user

router = APIRouter()


@router.post("/github", status_code=status.HTTP_200_OK)
async def github_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Handle GitHub webhooks"""
    return {"message": "GitHub webhook received"}


@router.post("/supabase", status_code=status.HTTP_200_OK)
async def supabase_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Handle Supabase webhooks"""
    return {"message": "Supabase webhook received"}


@router.post("/agent/{agent_id}", status_code=status.HTTP_200_OK)
async def agent_webhook(
    agent_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Handle agent-specific webhooks"""
    return {"message": f"Agent {agent_id} webhook received"}
