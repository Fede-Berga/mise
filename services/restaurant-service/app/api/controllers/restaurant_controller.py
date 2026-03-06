"""HTTP controller for the restaurant-service.

Responsibilities of this layer (and nothing more):
- Define routes and their HTTP semantics (status codes, response models)
- Wire dependency injection (DB session → repository → service)
- Translate service results into HTTP responses:
    - ``None``        → 404 Not Found
    - ``ValueError``  → 422 Unprocessable Entity (business rule violation)
    - success         → 200 / 201 / 204

No business logic lives here — it all belongs in :mod:`app.domain.services`.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from common.app.database import get_db_session
from common.app.dependencies import DbSessionDep, PaginationDep, TenantIdDep

from app.api.schemas import (
    RestaurantCreate,
    RestaurantRead,
    RestaurantUpdate,
    TableCreate,
    TableRead,
    TableUpdate,
)
from app.domain.services import RestaurantService, TableService
from app.infrastructure.repositories import RestaurantRepository, TableRepository

router = APIRouter()


# ---------------------------------------------------------------------------
# Dependency factories — wired by FastAPI's DI container
# ---------------------------------------------------------------------------


def _get_restaurant_repo(
    db: DbSessionDep,
    tenant_id: TenantIdDep,
) -> RestaurantRepository:
    """Construct a tenant-scoped restaurant repository."""
    return RestaurantRepository(db=db, tenant_id=tenant_id)


def _get_restaurant_service(
    repo: RestaurantRepository = Depends(_get_restaurant_repo),
) -> RestaurantService:
    """Construct the restaurant domain service."""
    return RestaurantService(repo=repo)


def _get_table_service(
    restaurant_id: int,
    db: DbSessionDep,
    tenant_id: TenantIdDep,
) -> TableService:
    """Construct the table domain service (scoped to both tenant and restaurant)."""
    restaurant_repo = RestaurantRepository(db=db, tenant_id=tenant_id)
    table_repo = TableRepository(db=db, restaurant_id=restaurant_id)
    return TableService(restaurant_repo=restaurant_repo, table_repo=table_repo)


# ---------------------------------------------------------------------------
# Restaurant endpoints
# ---------------------------------------------------------------------------


@router.get("/", response_model=list[RestaurantRead], summary="List restaurants")
def list_restaurants(
    pagination: PaginationDep,
    service: RestaurantService = Depends(_get_restaurant_service),
) -> list[RestaurantRead]:
    """Return all restaurants for the current tenant (paginated)."""
    return service.list_restaurants(skip=pagination.skip, limit=pagination.limit)


@router.post(
    "/",
    response_model=RestaurantRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a restaurant",
)
def create_restaurant(
    payload: RestaurantCreate,
    service: RestaurantService = Depends(_get_restaurant_service),
) -> RestaurantRead:
    """Create a new restaurant under the current tenant."""
    return service.create_restaurant(payload)


@router.get("/{restaurant_id}", response_model=RestaurantRead, summary="Get a restaurant")
def get_restaurant(
    restaurant_id: int,
    service: RestaurantService = Depends(_get_restaurant_service),
) -> RestaurantRead:
    """Return a single restaurant by id."""
    restaurant = service.get_restaurant(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return restaurant


@router.patch("/{restaurant_id}", response_model=RestaurantRead, summary="Update a restaurant")
def update_restaurant(
    restaurant_id: int,
    payload: RestaurantUpdate,
    service: RestaurantService = Depends(_get_restaurant_service),
) -> RestaurantRead:
    """Partially update a restaurant (PATCH semantics — only provided fields are changed)."""
    restaurant = service.update_restaurant(restaurant_id, payload)
    if not restaurant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return restaurant


@router.delete(
    "/{restaurant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a restaurant",
)
def delete_restaurant(
    restaurant_id: int,
    service: RestaurantService = Depends(_get_restaurant_service),
) -> None:
    """Delete a restaurant and all its tables."""
    if not service.delete_restaurant(restaurant_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")


# ---------------------------------------------------------------------------
# Table endpoints (nested under /{restaurant_id}/tables)
# ---------------------------------------------------------------------------


@router.get(
    "/{restaurant_id}/tables",
    response_model=list[TableRead],
    summary="List tables",
)
def list_tables(
    restaurant_id: int,
    pagination: PaginationDep,
    service: TableService = Depends(_get_table_service),
) -> list[TableRead]:
    """List all tables for a given restaurant."""
    try:
        return service.list_tables(restaurant_id, skip=pagination.skip, limit=pagination.limit)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/{restaurant_id}/tables",
    response_model=TableRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a table",
)
def add_table(
    restaurant_id: int,
    payload: TableCreate,
    service: TableService = Depends(_get_table_service),
) -> TableRead:
    """Add a new table to a restaurant."""
    try:
        return service.add_table(restaurant_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get(
    "/{restaurant_id}/tables/{table_id}",
    response_model=TableRead,
    summary="Get a table",
)
def get_table(
    restaurant_id: int,
    table_id: int,
    service: TableService = Depends(_get_table_service),
) -> TableRead:
    """Return a single table."""
    table = service.get_table(table_id)
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    return table


@router.patch(
    "/{restaurant_id}/tables/{table_id}",
    response_model=TableRead,
    summary="Update a table",
)
def update_table(
    restaurant_id: int,
    table_id: int,
    payload: TableUpdate,
    service: TableService = Depends(_get_table_service),
) -> TableRead:
    """Partially update a table (status, seats, label)."""
    table = service.update_table(table_id, payload)
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    return table


@router.delete(
    "/{restaurant_id}/tables/{table_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a table",
)
def remove_table(
    restaurant_id: int,
    table_id: int,
    service: TableService = Depends(_get_table_service),
) -> None:
    """Remove a table. Fails with 422 if the table is currently OCCUPIED."""
    try:
        if not service.remove_table(table_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    except ValueError as exc:
        # Business rule violation — table is occupied
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
