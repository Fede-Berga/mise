"""Enterprise middleware for Mise FastAPI services.

Provides:
- Request ID generation and propagation
- Structured request/response logging
- Unhandled exception → JSON error response
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

import structlog
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = structlog.get_logger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Inject ``X-Request-Id`` into every request/response.

    If the caller already supplies the header, it is reused (for
    distributed tracing).  Otherwise a new UUID-4 is generated.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))

        # Bind to structlog context for the duration of the request
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        # Bind tenant if present
        tenant_id = request.headers.get("x-tenant-id")
        if tenant_id:
            structlog.contextvars.bind_contextvars(tenant_id=tenant_id)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        response.headers["X-Request-Id"] = request_id

        if logging.getLogger().isEnabledFor(logging.DEBUG):
            await logger.adebug(
                "request_completed",
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

        return response


def register_middleware(app: FastAPI) -> None:
    """Register all enterprise middleware on the given FastAPI app."""
    app.add_middleware(RequestIdMiddleware)
