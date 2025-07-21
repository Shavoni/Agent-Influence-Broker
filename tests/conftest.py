"""Shared test fixtures and configuration."""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio

# Add the root directory to Python path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Override settings for testing."""
    settings = get_settings()
    settings.TESTING = True
    settings.DATABASE_URL = "postgresql://test:test@localhost:5432/test_db"
    return settings


@pytest.fixture
def mock_current_user():
    """Mock authenticated user for testing."""
    return {
        "id": "user-123",
        "email": "test@example.com",
        "role": "agent_owner",
        "is_active": True,
    }


@pytest.fixture
def sample_transaction_data() -> Dict[str, Any]:
    """Sample transaction data for testing."""
    return {
        "id": "txn-123",
        "from_agent_id": "agent-123",
        "to_agent_id": "agent-456",
        "amount": 1000.0,
        "currency": "USD",
        "status": "pending",
        "transaction_type": "negotiation_payment",
        "metadata": {"negotiation_id": "neg-123"},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_influence_data() -> Dict[str, Any]:
    """Sample influence metrics data for testing."""
    return {
        "agent_id": "agent-123",
        "influence_score": 85.5,
        "calculation_date": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "successful_negotiations": 15,
            "total_negotiations": 20,
            "average_deal_value": 5000.0,
            "network_connections": 25,
            "reputation_score": 85.5,
        },
    }
