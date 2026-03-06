"""FastAPI dependency providers shared across all Mise services.

FastAPI's dependency injection system is used throughout the codebase.
This module exports the most common typed ``Annotated`` dependencies so that
route functions stay concise and readable.

Example usage in a controller::

    @router.get("/items")
    def list_items(
        db: DbSessionDep,
        tenant_id: TenantIdDep,
        pagination: PaginationDep,
    ) -> list[ItemRead]:
        ...
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from common.app.auth import CurrentUser, get_current_user
from common.app.config import get_settings
from common.app.database import get_db_session

# ---------------------------------------------------------------------------
# Settings dependency
# ---------------------------------------------------------------------------

SettingsDep = Annotated[object, Depends(get_settings)]

# ---------------------------------------------------------------------------
# Database session dependency
# ---------------------------------------------------------------------------

DbSessionDep = Annotated[Session, Depends(get_db_session)]

# ---------------------------------------------------------------------------
# Tenant ID dependency
# ---------------------------------------------------------------------------


def get_tenant_id(
    settings=Depends(get_settings),
    current_user: CurrentUser = Depends(get_current_user),
    tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> str:
    """Extract the tenant ID from the ``X-Tenant-Id`` request header.

    In production Traefik should always inject this header after authenticating
    the Keycloak JWT. We deliberately do not fall back silently to a default
    tenant to avoid accidental cross-tenant access.
    """
    if not tenant_id:
        msg = "Missing tenant header"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    if current_user.tenant_id and tenant_id != current_user.tenant_id:
        msg = "Tenant header does not match token tenant"
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg)
    return tenant_id


TenantIdDep = Annotated[str, Depends(get_tenant_id)]

# ---------------------------------------------------------------------------
# Authenticated user dependency
# ---------------------------------------------------------------------------


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]

# ---------------------------------------------------------------------------
# Pagination dependency
# ---------------------------------------------------------------------------


class Pagination:
    """Encapsulates ``skip`` / ``limit`` query parameters for list endpoints.

    Attributes:
        skip:  Number of items to skip (offset). Defaults to 0.
        limit: Maximum number of items to return. Capped at 200.
    """

    def __init__(
        self,
        skip: int = Query(default=0, ge=0, description="Number of items to skip"),
        limit: int = Query(default=50, ge=1, le=200, description="Maximum items to return"),
    ) -> None:
        self.skip = skip
        self.limit = limit


PaginationDep = Annotated[Pagination, Depends(Pagination)]
