"""
Simple HTTP Server for Agent Influence Broker
Pure Python implementation without external dependencies
"""

import json
import logging
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

from .data_store import data_store

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentBrokerHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Agent Influence Broker API"""

    def _set_headers(self, status=200, content_type="application/json"):
        """Set HTTP response headers"""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS"
        )
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def _send_json_response(self, data: Dict[str, Any], status=200):
        """Send JSON response"""
        self._set_headers(status)
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode("utf-8"))

    def _send_error(self, status: int, message: str):
        """Send error response"""
        self._send_json_response(
            {
                "error": message,
                "status": status,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
            status,
        )

    def _parse_request_body(self) -> Optional[Dict[str, Any]]:
        """Parse JSON request body"""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                body = self.rfile.read(content_length).decode("utf-8")
                return json.loads(body)
            return None
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing request body: {e}")
            return None

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self._set_headers()

    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)

            # Convert query params from lists to single values
            params = {k: v[0] if v else None for k, v in query_params.items()}

            if path == "/":
                self._handle_root()
            elif path == "/health":
                self._handle_health()
            elif path == "/api/v1/agents":
                self._handle_list_agents(params)
            elif path.startswith("/api/v1/agents/"):
                agent_id = path.split("/")[-1]
                self._handle_get_agent(agent_id)
            elif path == "/api/v1/negotiations":
                self._handle_list_negotiations(params)
            elif path.startswith("/api/v1/negotiations/"):
                negotiation_id = path.split("/")[-1]
                self._handle_get_negotiation(negotiation_id)
            elif path == "/api/v1/transactions":
                self._handle_list_transactions(params)
            elif path.startswith("/api/v1/transactions/"):
                transaction_id = path.split("/")[-1]
                self._handle_get_transaction(transaction_id)
            else:
                self._send_error(404, "Not found")

        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self._send_error(500, "Internal server error")

    def do_POST(self):
        """Handle POST requests"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            body = self._parse_request_body()

            if body is None:
                self._send_error(400, "Invalid JSON in request body")
                return

            if path == "/api/v1/agents":
                self._handle_create_agent(body)
            elif path == "/api/v1/negotiations":
                self._handle_create_negotiation(body)
            elif path == "/api/v1/transactions":
                self._handle_create_transaction(body)
            else:
                self._send_error(404, "Not found")

        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self._send_error(500, "Internal server error")

    def _handle_root(self):
        """Handle root endpoint"""
        self._send_json_response(
            {
                "message": "Welcome to Agent Influence Broker",
                "version": "0.1.0",
                "status": "operational",
                "documentation": "/docs (FastAPI docs - not available in simple mode)",
                "api_version": "v1",
                "endpoints": {
                    "agents": "/api/v1/agents",
                    "negotiations": "/api/v1/negotiations",
                    "transactions": "/api/v1/transactions",
                },
            }
        )

    def _handle_health(self):
        """Handle health check endpoint"""
        self._send_json_response(
            {
                "status": "healthy",
                "version": "0.1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "uptime": "OK",
                "data_store": "in-memory",
                "sample_data": {
                    "agents": len(data_store.agents),
                    "negotiations": len(data_store.negotiations),
                    "transactions": len(data_store.transactions),
                },
            }
        )

    def _handle_list_agents(self, params: Dict[str, str]):
        """Handle list agents endpoint"""
        try:
            owner_id = params.get("owner_id")
            agent_type = params.get("agent_type")
            is_active = params.get("is_active")
            if is_active is not None:
                is_active = is_active.lower() == "true"

            limit = int(params.get("limit", 20))
            offset = int(params.get("offset", 0))

            agents, total = data_store.list_agents(
                owner_id=owner_id,
                agent_type=agent_type,
                is_active=is_active,
                limit=limit,
                offset=offset,
            )

            self._send_json_response(
                {
                    "agents": [agent.to_dict() for agent in agents],
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total,
                }
            )

        except ValueError as e:
            self._send_error(400, f"Invalid parameter: {e}")

    def _handle_get_agent(self, agent_id: str):
        """Handle get specific agent endpoint"""
        agent = data_store.get_agent(agent_id)
        if not agent:
            self._send_error(404, "Agent not found")
            return

        self._send_json_response(agent.to_dict())

    def _handle_create_agent(self, data: Dict[str, Any]):
        """Handle create agent endpoint"""
        try:
            # Basic validation
            required_fields = ["name", "agent_type"]
            for field in required_fields:
                if field not in data:
                    self._send_error(400, f"Missing required field: {field}")
                    return

            # For demo purposes, use a default owner_id
            owner_id = data.get("owner_id", "demo_user")

            agent = data_store.create_agent(data, owner_id)
            self._send_json_response(agent.to_dict(), 201)

        except ValueError as e:
            self._send_error(400, str(e))

    def _handle_list_negotiations(self, params: Dict[str, str]):
        """Handle list negotiations endpoint"""
        try:
            agent_id = params.get("agent_id")
            status = params.get("status")
            limit = int(params.get("limit", 20))
            offset = int(params.get("offset", 0))

            negotiations, total = data_store.list_negotiations(
                agent_id=agent_id, status=status, limit=limit, offset=offset
            )

            self._send_json_response(
                {
                    "negotiations": [nego.to_dict() for nego in negotiations],
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total,
                }
            )

        except ValueError as e:
            self._send_error(400, f"Invalid parameter: {e}")

    def _handle_get_negotiation(self, negotiation_id: str):
        """Handle get specific negotiation endpoint"""
        negotiation = data_store.get_negotiation(negotiation_id)
        if not negotiation:
            self._send_error(404, "Negotiation not found")
            return

        self._send_json_response(negotiation.to_dict())

    def _handle_create_negotiation(self, data: Dict[str, Any]):
        """Handle create negotiation endpoint"""
        try:
            # Basic validation
            required_fields = [
                "title",
                "initiator_agent_id",
                "responder_agent_id",
                "negotiation_type",
                "initial_proposal",
            ]
            for field in required_fields:
                if field not in data:
                    self._send_error(400, f"Missing required field: {field}")
                    return

            # Validate that agents exist
            initiator = data_store.get_agent(data["initiator_agent_id"])
            responder = data_store.get_agent(data["responder_agent_id"])

            if not initiator:
                self._send_error(400, "Initiator agent not found")
                return
            if not responder:
                self._send_error(400, "Responder agent not found")
                return

            negotiation = data_store.create_negotiation(data)
            self._send_json_response(negotiation.to_dict(), 201)

        except ValueError as e:
            self._send_error(400, str(e))

    def _handle_list_transactions(self, params: Dict[str, str]):
        """Handle list transactions endpoint"""
        try:
            agent_id = params.get("agent_id")
            status = params.get("status")
            limit = int(params.get("limit", 20))
            offset = int(params.get("offset", 0))

            transactions, total = data_store.list_transactions(
                agent_id=agent_id, status=status, limit=limit, offset=offset
            )

            self._send_json_response(
                {
                    "transactions": [tx.to_dict() for tx in transactions],
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total,
                }
            )

        except ValueError as e:
            self._send_error(400, f"Invalid parameter: {e}")

    def _handle_get_transaction(self, transaction_id: str):
        """Handle get specific transaction endpoint"""
        transaction = data_store.get_transaction(transaction_id)
        if not transaction:
            self._send_error(404, "Transaction not found")
            return

        self._send_json_response(transaction.to_dict())

    def _handle_create_transaction(self, data: Dict[str, Any]):
        """Handle create transaction endpoint"""
        try:
            # Basic validation
            required_fields = ["payer_agent_id", "payee_agent_id", "amount"]
            for field in required_fields:
                if field not in data:
                    self._send_error(400, f"Missing required field: {field}")
                    return

            # Validate that agents exist
            payer = data_store.get_agent(data["payer_agent_id"])
            payee = data_store.get_agent(data["payee_agent_id"])

            if not payer:
                self._send_error(400, "Payer agent not found")
                return
            if not payee:
                self._send_error(400, "Payee agent not found")
                return

            transaction = data_store.create_transaction(data)
            self._send_json_response(transaction.to_dict(), 201)

        except ValueError as e:
            self._send_error(400, str(e))

    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")


def run_server(host="0.0.0.0", port=8000):
    """Run the HTTP server"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, AgentBrokerHandler)

    logger.info(f"Agent Influence Broker starting on http://{host}:{port}")
    logger.info(f"Sample agents loaded: {len(data_store.agents)}")
    logger.info(f"Sample negotiations loaded: {len(data_store.negotiations)}")
    logger.info(f"Sample transactions loaded: {len(data_store.transactions)}")
    logger.info("Try these endpoints:")
    logger.info(f"  http://{host}:{port}/health")
    logger.info(f"  http://{host}:{port}/api/v1/agents")
    logger.info(f"  http://{host}:{port}/api/v1/negotiations")
    logger.info(f"  http://{host}:{port}/api/v1/transactions")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
        httpd.shutdown()


if __name__ == "__main__":
    run_server()
