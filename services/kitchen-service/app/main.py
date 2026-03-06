"""FastAPI application factory for the kitchen-service."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI

from common.app.auth import get_current_user
from common.app.config import get_settings
from common.app.events import subscribe_orders_placed, subscribe_orders_status_changed
from common.app.health import build_health_router
from common.app.logging import setup_logging
from common.app.middleware import register_middleware

from app.api.controllers.kitchen_controller import router as kitchen_router
from app.events_consumer import handle_orders_placed, handle_orders_status_changed

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(service_name=settings.service_name, log_level=settings.log_level, json_output=settings.log_json)

    tasks = [
        asyncio.create_task(subscribe_orders_placed(handle_orders_placed)),
        asyncio.create_task(subscribe_orders_status_changed(handle_orders_status_changed)),
    ]
    try:
        yield
    finally:
        for task in tasks:
            task.cancel()
        for task in tasks:
            try:
                await task
            except asyncio.CancelledError:
                pass


def create_app() -> FastAPI:
    """Construct the kitchen-service FastAPI application."""
    app = FastAPI(
        title="Mise Kitchen Service",
        description="Manages kitchen display tickets for order preparation tracking.",
        version="0.1.0",
        lifespan=lifespan,
    )
    register_middleware(app)
    app.include_router(build_health_router(service_name="kitchen-service"))
    app.include_router(
        kitchen_router,
        prefix="/kitchen/tickets",
        tags=["tickets"],
        dependencies=[Depends(get_current_user)],
    )
    return app


app = create_app()
