"""FastAPI application factory for the inventory-service."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI

from common.app.auth import get_current_user
from common.app.config import get_settings
from common.app.health import build_health_router
from common.app.logging import setup_logging
from common.app.middleware import register_middleware

from app.api.controllers.inventory_controller import router as inventory_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(service_name=settings.service_name, log_level=settings.log_level, json_output=settings.log_json)
    if not settings.log_json:
        from common.app.database import Base, engine  # noqa: PLC0415
        Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    """Construct the inventory-service FastAPI application."""
    app = FastAPI(
        title="Mise Inventory Service",
        description="Tracks stock levels, ingredients, and supplies with full movement audit trail.",
        version="0.1.0",
        lifespan=lifespan,
    )
    register_middleware(app)
    app.include_router(build_health_router(service_name="inventory-service"))
    app.include_router(
        inventory_router,
        prefix="/inventory",
        tags=["inventory"],
        dependencies=[Depends(get_current_user)],
    )
    return app


app = create_app()
