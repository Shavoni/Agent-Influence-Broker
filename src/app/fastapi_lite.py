"""
Enterprise FastAPI-compatible application for Agent Influence Broker
Production-ready implementation with advanced Python 3.14 compatibility
"""

import asyncio
import inspect
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class HTTPException:
    """HTTP Exception for error responses"""

    status_code: int
    detail: str


class Request:
    """Simple request object"""

    def __init__(
        self,
        method: str,
        path: str,
        query_params: Dict[str, str],
        body: Optional[str] = None,
    ):
        self.method = method
        self.path = path
        self.query_params = query_params
        self.body = body


class Response:
    """Simple response object"""

    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}


class FastAPILite:
    """Enterprise-grade FastAPI-compatible application framework"""

    def __init__(
        self, title: str = "FastAPI", version: str = "0.1.0", description: str = ""
    ):
        self.title = title
        self.version = version
        self.description = description
        self.routes: Dict[str, Dict[str, Callable]] = {}
        self.middleware = []

    def get(self, path: str, **kwargs):
        """Decorator for GET routes"""

        def decorator(func):
            if path not in self.routes:
                self.routes[path] = {}
            self.routes[path]["GET"] = func
            return func

        return decorator

    def post(self, path: str, **kwargs):
        """Decorator for POST routes"""

        def decorator(func):
            if path not in self.routes:
                self.routes[path] = {}
            self.routes[path]["POST"] = func
            return func

        return decorator

    def add_middleware(self, middleware_class, **kwargs):
        """Add middleware (simplified)"""
        self.middleware.append((middleware_class, kwargs))

    async def handle_request(self, request: Request) -> Response:
        """Handle incoming request"""
        try:
            # Find matching route
            handler = None
            path_params = {}

            # Exact match first
            if (
                request.path in self.routes
                and request.method in self.routes[request.path]
            ):
                handler = self.routes[request.path][request.method]
            else:
                # Try path parameter matching
                for route_path, methods in self.routes.items():
                    if request.method in methods:
                        # Simple path parameter matching for {param} style
                        if self._path_matches(route_path, request.path):
                            handler = methods[request.method]
                            path_params = self._extract_path_params(
                                route_path, request.path
                            )
                            break

            if not handler:
                return Response({"detail": "Not Found"}, status_code=404)

            # Call handler
            sig = inspect.signature(handler)
            kwargs = {}

            # Add query parameters if the handler expects them
            for param_name in sig.parameters:
                if param_name in request.query_params:
                    param_type = sig.parameters[param_name].annotation
                    value = request.query_params[param_name]

                    # Type conversion
                    if param_type == int:
                        kwargs[param_name] = int(value)
                    elif param_type == bool:
                        kwargs[param_name] = value.lower() == "true"
                    elif param_type == Optional[str] or param_type == str:
                        kwargs[param_name] = value if value else None
                    else:
                        kwargs[param_name] = value

            # Add path parameters
            kwargs.update(path_params)

            # Add request body for POST requests
            if request.method == "POST" and request.body:
                try:
                    body_data = json.loads(request.body)
                    # Look for a parameter that expects Dict[str, Any]
                    for param_name, param in sig.parameters.items():
                        if param.annotation == Dict[str, Any] or "Dict" in str(
                            param.annotation
                        ):
                            kwargs[param_name] = body_data
                            break
                except json.JSONDecodeError:
                    return Response({"detail": "Invalid JSON"}, status_code=400)

            # Call the handler
            if asyncio.iscoroutinefunction(handler):
                result = await handler(**kwargs)
            else:
                result = handler(**kwargs)

            return Response(result, status_code=200)

        except HTTPException as e:
            return Response({"detail": e.detail}, status_code=e.status_code)
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return Response({"detail": "Internal Server Error"}, status_code=500)

    def _path_matches(self, route_path: str, request_path: str) -> bool:
        """Check if route path matches request path with parameters"""
        route_parts = route_path.split("/")
        request_parts = request_path.split("/")

        if len(route_parts) != len(request_parts):
            return False

        for route_part, request_part in zip(route_parts, request_parts):
            if route_part.startswith("{") and route_part.endswith("}"):
                continue  # Parameter match
            elif route_part != request_part:
                return False

        return True

    def _extract_path_params(
        self, route_path: str, request_path: str
    ) -> Dict[str, str]:
        """Extract path parameters from request"""
        params = {}
        route_parts = route_path.split("/")
        request_parts = request_path.split("/")

        for route_part, request_part in zip(route_parts, request_parts):
            if route_part.startswith("{") and route_part.endswith("}"):
                param_name = route_part[1:-1]  # Remove { }
                params[param_name] = request_part

        return params


# Create the app instance
app = FastAPILite(
    title="Agent Influence Broker",
    version="0.1.0",
    description="A sophisticated platform where AI agents can negotiate, influence, and transact",
)

# Import our data store
from .data_store import data_store
