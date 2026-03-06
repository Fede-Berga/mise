"""FastAPI application factory for the order-service."""

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

from app.api.controllers.order_controller import router as order_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: initialises logging and dev-mode table creation."""
    settings = get_settings()
    setup_logging(service_name=settings.service_name, log_level=settings.log_level, json_output=settings.log_json)
    yield


def create_app() -> FastAPI:
    """Construct the order-service FastAPI application."""
    app = FastAPI(
        title="Mise Order Service",
        description=(
            "Manages the full order lifecycle: placement, item tracking, status updates, "
            "and domain event publishing (orders.placed, orders.status_changed)."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )
    register_middleware(app)
    app.include_router(build_health_router(service_name="order-service"))
    app.include_router(
        order_router,
        prefix="/orders",
        tags=["orders"],
        dependencies=[Depends(get_current_user)],
    )
    return app


app = create_app()
