"""FastAPI application factory for the hardware-service."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI

from common.app.auth import get_current_user
from common.app.config import get_settings
from common.app.health import build_health_router
from common.app.logging import setup_logging
from common.app.middleware import register_middleware

from app.api.controllers.hardware_controller import router as hardware_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(service_name=settings.service_name, log_level=settings.log_level, json_output=settings.log_json)
    if not settings.log_json:
        from common.app.database import Base, engine  # noqa: PLC0415

        Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    """Construct the hardware-service FastAPI application."""
    app = FastAPI(
        title="Mise Hardware Service",
        description="Manages POS terminals, kitchen displays, and other peripheral devices.",
        version="0.1.0",
        lifespan=lifespan,
    )
    register_middleware(app)
    app.include_router(build_health_router(service_name="hardware-service"))
    app.include_router(
        hardware_router,
        prefix="/devices",
        tags=["devices"],
        dependencies=[Depends(get_current_user)],
    )
    return app


app = create_app()
