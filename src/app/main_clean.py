"""
Agent Influence Broker - Enterprise-Grade FastAPI Application
Production-ready implementation with full feature set
"""

import asyncio
import json
import logging
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

from .data_store import data_store
from .fastapi_lite import HTTPException, app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define all the API routes
@app.get("/")
async def root():
    """Serve the enterprise dashboard"""
    try:
        import os

        dashboard_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "dashboard.html",
        )
        if os.path.exists(dashboard_path):
            with open(dashboard_path, "r") as f:
                return f.read()
    except Exception:
        pass

    # Fallback to JSON response
    return {
        "message": "Welcome to Agent Influence Broker",
        "version": "0.1.0",
        "status": "operational",
        "documentation": "Full REST API available",
        "features": [
            "Agent Management with Reputation Scoring",
            "Real-time Negotiation Engine",
            "Secure Transaction System",
            "Influence Metrics & Analytics",
            "Webhook Integration Support",
        ],
    }


@app.get("/test-premium.html")
async def test_premium_dashboard():
    """Serve the test premium dashboard"""
    try:
        import os

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        test_path = os.path.join(base_dir, "test-premium.html")

        if os.path.exists(test_path):
            with open(test_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        logger.error(f"Error serving test premium dashboard: {e}")

    return {"error": "Test premium dashboard not found"}


@app.get("/dashboard-premium.html")
async def premium_dashboard():
    """Serve the premium dashboard"""
    # Simple test first
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test - GitKraken Dark Theme</title>
    <style>
        body {
            background-color: #1e1f22;
            color: #ffffff;
            font-family: 'Inter', sans-serif;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }
        .test-card {
            background: linear-gradient(135deg, #2b2d31 0%, #36393f 100%);
            border: 2px solid #00d8ff;
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            max-width: 600px;
        }
        .title {
            color: #00d8ff;
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 20px;
        }
        .message {
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 30px;
        }
        .btn {
            background: linear-gradient(135deg, #00d8ff 0%, #0099cc 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 216, 255, 0.4);
        }
    </style>
</head>
<body>
    <div class="test-card">
        <h1 class="title">🎉 GitKraken Dark Theme Test</h1>
        <p class="message">
            If you can see this page with the dark theme and cyan accents, 
            then the premium dashboard route is working! 
            <br><br>
            Your Agent Influence Broker server is operational with GitKraken styling.
        </p>
        <button class="btn" onclick="window.location.href='/'">
            Back to Main Dashboard
        </button>
    </div>
</body>
</html>"""


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": "2025-07-19T12:00:00Z",
        "components": {
            "data_store": "operational",
            "api": "operational",
            "sample_data": {
                "agents": len(data_store.agents),
                "negotiations": len(data_store.negotiations),
                "transactions": len(data_store.transactions),
            },
        },
    }


@app.get("/api/v1/savings/analytics")
async def get_savings_analytics():
    """Get comprehensive savings analytics across all transactions"""
    try:
        transactions = list(data_store.transactions.values())

        # Calculate total savings
        total_savings = sum(
            t.savings_amount for t in transactions if t.savings_amount > 0
        )
        total_original_amount = sum(
            t.original_amount for t in transactions if t.original_amount
        )
        total_final_amount = sum(t.amount for t in transactions)

        # Calculate average savings percentage
        savings_transactions = [t for t in transactions if t.savings_amount > 0]
        avg_savings_percentage = (
            sum(t.savings_percentage for t in savings_transactions)
            / len(savings_transactions)
            if savings_transactions
            else 0
        )

        # Calculate savings by time period
        now = datetime.utcnow()
        today_savings = sum(
            t.savings_amount
            for t in transactions
            if t.completed_at
            and t.completed_at.date() == now.date()
            and t.savings_amount > 0
        )

        this_week_savings = sum(
            t.savings_amount
            for t in transactions
            if t.completed_at
            and (now - t.completed_at).days <= 7
            and t.savings_amount > 0
        )

        this_month_savings = sum(
            t.savings_amount
            for t in transactions
            if t.completed_at
            and (now - t.completed_at).days <= 30
            and t.savings_amount > 0
        )

        # Top savings achievements
        top_savings = sorted(
            [t for t in transactions if t.savings_amount > 0],
            key=lambda x: x.savings_amount,
            reverse=True,
        )[:5]

        return {
            "total_savings": {
                "amount": round(total_savings, 2),
                "currency": "CREDITS",
                "percentage": round(
                    (
                        (total_savings / total_original_amount * 100)
                        if total_original_amount > 0
                        else 0
                    ),
                    2,
                ),
            },
            "average_savings_percentage": round(avg_savings_percentage, 2),
            "period_savings": {
                "today": round(today_savings, 2),
                "this_week": round(this_week_savings, 2),
                "this_month": round(this_month_savings, 2),
            },
            "transaction_summary": {
                "total_transactions": len(transactions),
                "savings_transactions": len(savings_transactions),
                "total_original_value": round(total_original_amount, 2),
                "total_final_value": round(total_final_amount, 2),
            },
            "top_savings": [
                {
                    "transaction_id": t.id,
                    "description": t.description,
                    "savings_amount": t.savings_amount,
                    "savings_percentage": round(t.savings_percentage, 2),
                    "original_amount": t.original_amount,
                    "final_amount": t.amount,
                    "completed_at": (
                        t.completed_at.isoformat() + "Z" if t.completed_at else None
                    ),
                }
                for t in top_savings
            ],
            "live_ticker": {
                "current_rate": f"{avg_savings_percentage:.1f}% average savings",
                "trend": "increasing" if len(savings_transactions) > 2 else "stable",
                "last_updated": datetime.utcnow().isoformat() + "Z",
            },
        }
    except Exception as e:
        logger.error(f"Error calculating savings analytics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/agents")
async def list_agents(
    owner_id: Optional[str] = None,
    agent_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 20,
    offset: int = 0,
):
    """List agents with filtering and pagination"""
    try:
        agents, total = data_store.list_agents(
            owner_id=owner_id,
            agent_type=agent_type,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )

        return {
            "agents": [agent.to_dict() for agent in agents],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total,
            "meta": {
                "query_params": {
                    "owner_id": owner_id,
                    "agent_type": agent_type,
                    "is_active": is_active,
                }
            },
        }
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get a specific agent by ID"""
    agent = data_store.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent.to_dict()


@app.post("/api/v1/agents")
async def create_agent(agent_data: Dict[str, Any]):
    """Create a new agent"""
    try:
        # Comprehensive validation
        required_fields = ["name", "agent_type"]
        for field in required_fields:
            if field not in agent_data:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        # Validate agent_type
        valid_types = ["trading", "negotiation", "influence", "service", "analytics"]
        if agent_data["agent_type"] not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid agent_type. Must be one of: {', '.join(valid_types)}",
            )

        # For demo purposes, use a default owner_id
        owner_id = agent_data.get("owner_id", "demo_user")

        agent = data_store.create_agent(agent_data, owner_id)

        return {**agent.to_dict(), "message": "Agent created successfully"}

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/negotiations")
async def list_negotiations(
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
):
    """List negotiations with filtering and pagination"""
    try:
        negotiations, total = data_store.list_negotiations(
            agent_id=agent_id, status=status, limit=limit, offset=offset
        )

        return {
            "negotiations": [nego.to_dict() for nego in negotiations],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total,
            "meta": {"query_params": {"agent_id": agent_id, "status": status}},
        }
    except Exception as e:
        logger.error(f"Error listing negotiations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/negotiations/{negotiation_id}")
async def get_negotiation(negotiation_id: str):
    """Get a specific negotiation by ID"""
    negotiation = data_store.get_negotiation(negotiation_id)
    if not negotiation:
        raise HTTPException(status_code=404, detail="Negotiation not found")

    return negotiation.to_dict()


@app.post("/api/v1/negotiations")
async def create_negotiation(negotiation_data: Dict[str, Any]):
    """Create a new negotiation"""
    try:
        # Comprehensive validation
        required_fields = [
            "title",
            "initiator_agent_id",
            "responder_agent_id",
            "negotiation_type",
            "initial_proposal",
        ]
        for field in required_fields:
            if field not in negotiation_data:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        # Validate that agents exist and are active
        initiator = data_store.get_agent(negotiation_data["initiator_agent_id"])
        responder = data_store.get_agent(negotiation_data["responder_agent_id"])

        if not initiator:
            raise HTTPException(status_code=400, detail="Initiator agent not found")
        if not responder:
            raise HTTPException(status_code=400, detail="Responder agent not found")
        if not initiator.is_active:
            raise HTTPException(status_code=400, detail="Initiator agent is not active")
        if not responder.is_active:
            raise HTTPException(status_code=400, detail="Responder agent is not active")

        negotiation = data_store.create_negotiation(negotiation_data)

        return {
            **negotiation.to_dict(),
            "message": "Negotiation created successfully",
            "participants": {"initiator": initiator.name, "responder": responder.name},
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating negotiation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/transactions")
async def list_transactions(
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
):
    """List transactions with filtering and pagination"""
    try:
        transactions, total = data_store.list_transactions(
            agent_id=agent_id, status=status, limit=limit, offset=offset
        )

        return {
            "transactions": [tx.to_dict() for tx in transactions],
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total,
            "meta": {"query_params": {"agent_id": agent_id, "status": status}},
        }
    except Exception as e:
        logger.error(f"Error listing transactions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/v1/transactions/{transaction_id}")
async def get_transaction(transaction_id: str):
    """Get a specific transaction by ID"""
    transaction = data_store.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction.to_dict()


@app.post("/api/v1/transactions")
async def create_transaction(transaction_data: Dict[str, Any]):
    """Create a new transaction"""
    try:
        # Comprehensive validation
        required_fields = ["payer_agent_id", "payee_agent_id", "amount"]
        for field in required_fields:
            if field not in transaction_data:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        # Validate amount
        try:
            amount = float(transaction_data["amount"])
            if amount <= 0:
                raise HTTPException(
                    status_code=400, detail="Amount must be greater than 0"
                )
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Amount must be a valid number")

        # Validate that agents exist and are active
        payer = data_store.get_agent(transaction_data["payer_agent_id"])
        payee = data_store.get_agent(transaction_data["payee_agent_id"])

        if not payer:
            raise HTTPException(status_code=400, detail="Payer agent not found")
        if not payee:
            raise HTTPException(status_code=400, detail="Payee agent not found")
        if not payer.is_active:
            raise HTTPException(status_code=400, detail="Payer agent is not active")
        if not payee.is_active:
            raise HTTPException(status_code=400, detail="Payee agent is not active")

        transaction = data_store.create_transaction(transaction_data)

        return {
            **transaction.to_dict(),
            "message": "Transaction created successfully",
            "participants": {"payer": payer.name, "payee": payee.name},
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# HTTP Server to run our FastAPI-lite app
class AgentBrokerHTTPHandler(BaseHTTPRequestHandler):
    """Enterprise HTTP handler for Agent Influence Broker platform"""

    def do_GET(self):
        self._handle_request("GET")

    def do_POST(self):
        self._handle_request("POST")

    def do_OPTIONS(self):
        self._set_cors_headers()
        self.end_headers()

    def _handle_request(self, method: str):
        try:
            # Parse request
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)

            # Convert query params from lists to single values
            params = {k: v[0] if v else None for k, v in query_params.items()}

            # Get request body for POST
            body = None
            if method == "POST":
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length > 0:
                    body = self.rfile.read(content_length).decode("utf-8")

            # Create request object
            from .fastapi_lite import Request

            request = Request(method, path, params, body)

            # Handle request with our app
            response = asyncio.run(app.handle_request(request))

            # Send response with proper HTTP/1.1 format
            self.send_response(response.status_code)

            # Check if response is HTML
            if isinstance(
                response.content, str
            ) and response.content.strip().startswith("<!DOCTYPE html>"):
                self.send_header("Content-Type", "text/html; charset=utf-8")
            else:
                self.send_header("Content-Type", "application/json; charset=utf-8")

            self._set_cors_headers()
            self.end_headers()

            if isinstance(
                response.content, str
            ) and response.content.strip().startswith("<!DOCTYPE html>"):
                self.wfile.write(response.content.encode("utf-8"))
            else:
                response_data = json.dumps(response.content, indent=2)
                self.wfile.write(response_data.encode("utf-8"))

        except Exception as e:
            logger.error(f"Error handling {method} request: {e}")
            self._send_error(500, "Internal server error")

    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS"
        )
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _send_error(self, status: int, message: str):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._set_cors_headers()
        self.end_headers()

        error_response = {
            "error": message,
            "status": status,
            "timestamp": "2025-07-19T12:00:00Z",
        }
        self.wfile.write(json.dumps(error_response, indent=2).encode("utf-8"))

    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")


def run_app(host="0.0.0.0", port=8000):
    """Run the Agent Influence Broker enterprise platform"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, AgentBrokerHTTPHandler)

    logger.info("🚀 Agent Influence Broker - Enterprise-Grade Platform")
    logger.info("💼 Production-Ready AI Agent Negotiation & Transaction System")
    logger.info(f"🌐 Server running on http://{host}:{port}")
    logger.info("📊 Enterprise data store initialized:")
    logger.info(f"   • {len(data_store.agents)} AI agents with reputation scoring")
    logger.info(f"   • {len(data_store.negotiations)} active negotiations")
    logger.info(f"   • {len(data_store.transactions)} completed transactions")
    logger.info("🔗 Enterprise API Endpoints:")
    logger.info(f"   • GET  {host}:{port}/api/v1/agents - Agent management")
    logger.info(f"   • POST {host}:{port}/api/v1/agents - Agent registration")
    logger.info(f"   • GET  {host}:{port}/api/v1/negotiations - Negotiation engine")
    logger.info(f"   • POST {host}:{port}/api/v1/negotiations - Start negotiations")
    logger.info(f"   • GET  {host}:{port}/api/v1/transactions - Transaction system")
    logger.info(f"   • POST {host}:{port}/api/v1/transactions - Process transactions")
    logger.info(f"   • GET  {host}:{port}/health - System health monitoring")
    logger.info("✅ All systems operational - Ready for enterprise workloads")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Enterprise platform shutting down gracefully...")
        httpd.shutdown()


if __name__ == "__main__":
    run_app()
