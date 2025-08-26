"""
API Gateway for Rust Crate Pipeline Microservices

Provides:
- Service discovery and routing
- Load balancing
- Authentication and authorization
- Rate limiting
- Request/response transformation
- Health checks and monitoring
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp
import jwt
from aiohttp import web
from prometheus_client import Counter, Gauge, Histogram


@dataclass
class ServiceEndpoint:
    """Represents a microservice endpoint."""

    name: str
    url: str
    health_check_url: str
    weight: int = 1
    max_requests: int = 100
    current_requests: int = 0
    is_healthy: bool = True
    last_health_check: float = 0.0
    response_time_avg: float = 0.0


class ServiceRegistry:
    """Service discovery and registry."""

    def __init__(self):
        self.services: Dict[str, List[ServiceEndpoint]] = {}
        self.logger = logging.getLogger(__name__)

    def register_service(self, service_name: str, endpoint: ServiceEndpoint) -> None:
        """Register a service endpoint."""
        if service_name not in self.services:
            self.services[service_name] = []
        self.services[service_name].append(endpoint)
        self.logger.info(f"Registered service {service_name} at {endpoint.url}")

    def get_service_endpoints(self, service_name: str) -> List[ServiceEndpoint]:
        """Get all endpoints for a service."""
        return self.services.get(service_name, [])

    def get_healthy_endpoints(self, service_name: str) -> List[ServiceEndpoint]:
        """Get healthy endpoints for a service."""
        endpoints = self.get_service_endpoints(service_name)
        return [ep for ep in endpoints if ep.is_healthy]

    async def health_check_all(self) -> None:
        """Perform health checks on all services."""
        for service_name, endpoints in self.services.items():
            for endpoint in endpoints:
                await self._health_check_endpoint(endpoint)

    async def _health_check_endpoint(self, endpoint: ServiceEndpoint) -> None:
        """Check health of a single endpoint."""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(
                    endpoint.health_check_url, timeout=5
                ) as response:
                    response_time = time.time() - start_time
                    endpoint.is_healthy = response.status == 200
                    endpoint.response_time_avg = response_time
                    endpoint.last_health_check = time.time()
        except Exception as e:
            endpoint.is_healthy = False
            self.logger.warning(f"Health check failed for {endpoint.url}: {e}")


class LoadBalancer:
    """Load balancer with multiple strategies."""

    def __init__(self, strategy: str = "round_robin"):
        self.strategy = strategy
        self.current_index = 0
        self.logger = logging.getLogger(__name__)

    def select_endpoint(
        self, endpoints: List[ServiceEndpoint]
    ) -> Optional[ServiceEndpoint]:
        """Select an endpoint based on load balancing strategy."""
        if not endpoints:
            return None

        if self.strategy == "round_robin":
            return self._round_robin(endpoints)
        elif self.strategy == "least_connections":
            return self._least_connections(endpoints)
        elif self.strategy == "weighted":
            return self._weighted(endpoints)
        else:
            return endpoints[0]

    def _round_robin(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Round-robin load balancing."""
        endpoint = endpoints[self.current_index % len(endpoints)]
        self.current_index += 1
        return endpoint

    def _least_connections(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Least connections load balancing."""
        return min(endpoints, key=lambda ep: ep.current_requests)

    def _weighted(self, endpoints: List[ServiceEndpoint]) -> ServiceEndpoint:
        """Weighted load balancing."""
        total_weight = sum(ep.weight for ep in endpoints)
        if total_weight == 0:
            return endpoints[0]

        # Simple weighted selection
        import random

        rand = random.uniform(0, total_weight)
        current_weight = 0

        for endpoint in endpoints:
            current_weight += endpoint.weight
            if rand <= current_weight:
                return endpoint

        return endpoints[-1]


class RateLimiter:
    """Rate limiting implementation."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = {}
        self.logger = logging.getLogger(__name__)

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed."""
        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time
                for req_time in self.requests[client_id]
                if req_time > minute_ago
            ]
        else:
            self.requests[client_id] = []

        # Check rate limit
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False

        # Add current request
        self.requests[client_id].append(now)
        return True


class APIGateway:
    """Main API Gateway implementation."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Core components
        self.service_registry = ServiceRegistry()
        self.load_balancer = LoadBalancer(
            config.get("load_balancer_strategy", "round_robin")
        )
        self.rate_limiter = RateLimiter(config.get("rate_limit_per_minute", 60))

        # Metrics
        self.request_counter = Counter(
            "api_requests_total", "Total API requests", ["service", "status"]
        )
        self.request_duration = Histogram(
            "api_request_duration_seconds", "Request duration", ["service"]
        )
        self.active_connections = Gauge(
            "api_active_connections", "Active connections", ["service"]
        )

        # JWT secret for authentication
        self.jwt_secret = config.get("jwt_secret", "your-secret-key")

        # Initialize services
        self._register_default_services()

    def _register_default_services(self) -> None:
        """Register default microservices."""
        services_config = self.config.get("services", {})

        for service_name, service_config in services_config.items():
            endpoints = service_config.get("endpoints", [])
            for endpoint_config in endpoints:
                endpoint = ServiceEndpoint(
                    name=service_name,
                    url=endpoint_config["url"],
                    health_check_url=endpoint_config.get(
                        "health_check", f"{endpoint_config['url']}/health"
                    ),
                    weight=endpoint_config.get("weight", 1),
                    max_requests=endpoint_config.get("max_requests", 100),
                )
                self.service_registry.register_service(service_name, endpoint)

    async def handle_request(self, request: web.Request) -> web.Response:
        """Handle incoming API request."""
        start_time = time.time()

        try:
            # Extract service name from path
            path_parts = request.path.strip("/").split("/")
            if not path_parts:
                return web.json_response({"error": "Invalid path"}, status=400)

            service_name = path_parts[0]

            # Rate limiting
            client_id = self._get_client_id(request)
            if not self.rate_limiter.is_allowed(client_id):
                self.request_counter.labels(service=service_name, status="429").inc()
                return web.json_response({"error": "Rate limit exceeded"}, status=429)

            # Authentication
            auth_result = await self._authenticate_request(request)
            if not auth_result["authenticated"]:
                self.request_counter.labels(service=service_name, status="401").inc()
                return web.json_response({"error": "Unauthorized"}, status=401)

            # Get service endpoint
            endpoints = self.service_registry.get_healthy_endpoints(service_name)
            if not endpoints:
                self.request_counter.labels(service=service_name, status="503").inc()
                return web.json_response({"error": "Service unavailable"}, status=503)

            # Select endpoint
            endpoint = self.load_balancer.select_endpoint(endpoints)
            if not endpoint:
                self.request_counter.labels(service=service_name, status="503").inc()
                return web.json_response(
                    {"error": "No available endpoints"}, status=503
                )

            # Update connection count
            endpoint.current_requests += 1
            self.active_connections.labels(service=service_name).inc()

            try:
                # Forward request
                response = await self._forward_request(request, endpoint, service_name)

                # Update metrics
                duration = time.time() - start_time
                self.request_duration.labels(service=service_name).observe(duration)
                self.request_counter.labels(
                    service=service_name, status=str(response.status)
                ).inc()

                return response

            finally:
                # Update connection count
                endpoint.current_requests -= 1
                self.active_connections.labels(service=service_name).dec()

        except Exception as e:
            self.logger.error(f"Request handling error: {e}")
            self.request_counter.labels(service="unknown", status="500").inc()
            return web.json_response({"error": "Internal server error"}, status=500)

    async def _forward_request(
        self, request: web.Request, endpoint: ServiceEndpoint, service_name: str
    ) -> web.Response:
        """Forward request to service endpoint."""
        # Build target URL
        target_path = "/".join(request.path.strip("/").split("/")[1:])
        target_url = urljoin(endpoint.url, target_path)

        # Prepare headers
        headers = dict(request.headers)
        headers.pop("Host", None)  # Remove host header

        # Prepare request data
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.read()
        else:
            body = None

        # Forward request
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=body,
                params=request.query_string,
                timeout=30,
            ) as response:
                # Read response
                response_data = await response.read()

                # Create response
                return web.Response(
                    body=response_data,
                    status=response.status,
                    headers=dict(response.headers),
                )

    async def _authenticate_request(self, request: web.Request) -> Dict[str, Any]:
        """Authenticate incoming request."""
        try:
            # Check for API key in headers
            api_key = request.headers.get("X-API-Key")
            if api_key:
                # Validate API key (implement your logic)
                valid_keys = self.config.get("api_keys", [])
                if api_key in valid_keys:
                    return {
                        "authenticated": True,
                        "user_id": "api_user",
                        "method": "api_key",
                    }

            # Check for JWT token
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                try:
                    payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
                    return {
                        "authenticated": True,
                        "user_id": payload.get("sub"),
                        "method": "jwt",
                    }
                except jwt.InvalidTokenError:
                    return {"authenticated": False, "error": "Invalid token"}

            # Public endpoints (no auth required)
            public_endpoints = self.config.get(
                "public_endpoints", ["/health", "/metrics"]
            )
            if any(request.path.startswith(ep) for ep in public_endpoints):
                return {
                    "authenticated": True,
                    "user_id": "anonymous",
                    "method": "public",
                }

            return {"authenticated": False, "error": "No authentication provided"}

        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return {"authenticated": False, "error": "Authentication failed"}

    def _get_client_id(self, request: web.Request) -> str:
        """Extract client ID for rate limiting."""
        # Try to get user ID from various sources
        user_id = request.headers.get("X-User-ID")
        if user_id:
            return f"user:{user_id}"

        # Use API key if available
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api:{api_key[:8]}"

        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"

        # Use remote address
        remote = request.remote or "unknown"
        return f"ip:{remote}"

    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint."""
        return web.json_response(
            {
                "status": "healthy",
                "services": {
                    name: len(self.service_registry.get_healthy_endpoints(name))
                    for name in self.service_registry.services.keys()
                },
            }
        )

    async def metrics(self, request: web.Request) -> web.Response:
        """Prometheus metrics endpoint."""
        from prometheus_client import generate_latest

        return web.Response(body=generate_latest(), content_type="text/plain")


async def create_app(config: Dict[str, Any]) -> web.Application:
    """Create API Gateway application."""
    app = web.Application()

    # Create gateway
    gateway = APIGateway(config)

    # Add routes
    app.router.add_get("/health", gateway.health_check)
    app.router.add_get("/metrics", gateway.metrics)
    app.router.add_route("*", "/{path:.*}", gateway.handle_request)

    # Start health check background task
    async def health_check_task():
        while True:
            await gateway.service_registry.health_check_all()
            await asyncio.sleep(30)  # Check every 30 seconds

    app.on_startup.append(lambda app: asyncio.create_task(health_check_task()))

    return app


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="API Gateway")
    parser.add_argument(
        "--config", default="gateway_config.json", help="Configuration file"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")

    args = parser.parse_args()

    # Load configuration
    with open(args.config, "r") as f:
        config = json.load(f)

    # Create and run app
    app = asyncio.run(create_app(config))
    web.run_app(app, host=args.host, port=args.port)
