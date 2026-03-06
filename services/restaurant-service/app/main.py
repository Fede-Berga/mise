"""FastAPI application factory for the restaurant-service.

Uses a lifespan context manager for startup/shutdown tasks (NATS connection,
DB table creation in development mode).

The ``create_app`` factory pattern allows tests to spin up the app without
starting the full NATS/DB infrastructure.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from common.app.config import get_settings
from common.app.health import build_health_router
from common.app.logging import setup_logging
from common.app.middleware import register_middleware
from common.app.auth import get_current_user
from fastapi import Depends

from app.api.controllers.restaurant_controller import router as restaurant_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: runs startup logic before yielding, teardown after."""
    settings = get_settings()
    setup_logging(service_name=settings.service_name, log_level=settings.log_level, json_output=settings.log_json)
    yield
    # Teardown: nothing required yet; NATS publisher would be drained here.


def create_app() -> FastAPI:
    """Construct and configure the restaurant-service FastAPI application."""
    app = FastAPI(
        title="Mise Restaurant Service",
        description="Manages restaurants and their dining tables for a multi-tenant deployment.",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Register shared enterprise middleware (request ID, structured logging)
    register_middleware(app)

    # Health probes — /healthz (liveness) and /readyz (readiness with DB check)
    app.include_router(build_health_router(service_name="restaurant-service"))

    # Domain routes
    app.include_router(
        restaurant_router,
        prefix="/restaurants",
        tags=["restaurants"],
        dependencies=[Depends(get_current_user)],
    )

    return app


app = create_app()
