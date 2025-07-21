"""
Simplified FastAPI Application Entry Point for Testing
Agent Influence Broker - Basic functionality test
"""

from typing import Any, Dict

from fastapi import FastAPI

# Create a simple FastAPI app for testing
app = FastAPI(
    title="Agent Influence Broker",
    version="0.1.0",
    description="A platform where AI agents can negotiate, influence, and transact with each other.",
)


@app.get("/")
async def root() -> Dict[str, Any]:
    """Welcome message"""
    return {
        "message": "🚀 Welcome to Agent Influence Broker",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs",
        "features": [
            "Agent Management",
            "Negotiation Engine",
            "Influence Metrics",
            "Transaction System",
            "Webhook Integration",
        ],
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": "2025-07-19T12:00:00Z",
        "services": {
            "api": "operational",
            "database": "pending_setup",
            "cache": "pending_setup",
        },
    }


@app.get("/api/v1/agents/")
async def list_agents() -> Dict[str, Any]:
    """List agents (mock endpoint)"""
    return {
        "agents": [
            {
                "id": "agent-001",
                "name": "Trading Agent Alpha",
                "type": "trading",
                "reputation_score": 95.5,
                "influence_score": 88.2,
                "is_active": True,
                "is_verified": True,
            },
            {
                "id": "agent-002",
                "name": "Negotiation Bot Beta",
                "type": "negotiation",
                "reputation_score": 92.1,
                "influence_score": 85.7,
                "is_active": True,
                "is_verified": True,
            },
        ],
        "total": 2,
        "page": 1,
        "size": 20,
    }


@app.get("/api/v1/negotiations/")
async def list_negotiations() -> Dict[str, Any]:
    """List negotiations (mock endpoint)"""
    return {
        "negotiations": [
            {
                "id": "neg-001",
                "title": "Resource Exchange Agreement",
                "status": "active",
                "phase": "bargaining",
                "participants": ["agent-001", "agent-002"],
                "created_at": "2025-07-19T10:30:00Z",
            }
        ],
        "total": 1,
        "page": 1,
        "size": 20,
    }


@app.get("/api/v1/transactions/")
async def list_transactions() -> Dict[str, Any]:
    """List transactions (mock endpoint)"""
    return {
        "transactions": [
            {
                "id": "tx-001",
                "amount": 1250.50,
                "currency": "CREDITS",
                "status": "completed",
                "payer": "agent-001",
                "payee": "agent-002",
                "created_at": "2025-07-19T11:15:00Z",
            }
        ],
        "total": 1,
        "page": 1,
        "size": 20,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
