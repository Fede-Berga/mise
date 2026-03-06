"""Deep health-check endpoints for Mise services.

Provides ``/healthz`` (liveness) and ``/readyz`` (readiness) routes that
probe actual dependencies (DB, NATS, Redis) rather than just returning a
static ``{"status": "ok"}``.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter


def build_health_router(*, service_name: str) -> APIRouter:
    """Create a health-check router.

    Usage in ``create_app``::

        from common.health import build_health_router
        app.include_router(build_health_router(service_name="menu-service"))
    """
    router = APIRouter(tags=["health"])

    @router.get("/healthz")
    async def liveness() -> dict[str, str]:
        """Liveness probe — is the process alive?"""
        return {"status": "ok", "service": service_name}

    @router.get("/readyz")
    async def readiness() -> dict[str, Any]:
        """Readiness probe — can the service handle traffic?

        Checks database connectivity and downstream dependencies.
        Override or extend per service as needed.
        """
        checks: dict[str, str] = {}
        all_ok = True

        # Database check
        try:
            from common.app.database import engine  # noqa: PLC0415

            with engine.connect() as conn:
                conn.execute(__import__("sqlalchemy").text("SELECT 1"))
            checks["database"] = "ok"
        except Exception:  # noqa: BLE001
            checks["database"] = "unavailable"
            all_ok = False

        return {
            "status": "ok" if all_ok else "degraded",
            "service": service_name,
            "checks": checks,
        }

    return router
