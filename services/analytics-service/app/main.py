"""FastAPI application factory for the analytics-service."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI

from common.app.auth import get_current_user
from common.app.config import get_settings
from common.app.health import build_health_router
from common.app.logging import setup_logging
from common.app.middleware import register_middleware

from app.api.controllers.analytics_controller import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(service_name=settings.service_name, log_level=settings.log_level, json_output=settings.log_json)
    yield  # Analytics is read-only; no DB table creation needed


def create_app() -> FastAPI:
    """Construct the analytics-service FastAPI application."""
    app = FastAPI(
        title="Mise Analytics Service",
        description="Provides aggregated order statistics and KPI dashboards for restaurants.",
        version="0.1.0",
        lifespan=lifespan,
    )
    register_middleware(app)
    app.include_router(build_health_router(service_name="analytics-service"))
    app.include_router(
        analytics_router,
        prefix="/analytics",
        tags=["analytics"],
        dependencies=[Depends(get_current_user)],
    )
    return app


app = create_app()
