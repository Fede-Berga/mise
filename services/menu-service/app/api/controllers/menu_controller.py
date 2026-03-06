"""HTTP controller for the menu-service.

CRUD operations for menu items, scoped to a restaurant and tenant.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from common.app.dependencies import DbSessionDep, TenantIdDep

from app.api.schemas import MenuItemCreate, MenuItemRead, MenuItemUpdate
from app.domain.services import MenuService
from app.infrastructure.repositories import MenuRepository

router = APIRouter()


# ---------------------------------------------------------------------------
# Dependency factories
# ---------------------------------------------------------------------------


def _get_menu_repo(db: DbSessionDep, tenant_id: TenantIdDep) -> MenuRepository:
    """Construct a tenant-scoped menu repository."""
    return MenuRepository(db=db, tenant_id=tenant_id)


def _get_service(repo: MenuRepository = Depends(_get_menu_repo)) -> MenuService:
    """Construct the menu domain service."""
    return MenuService(repo=repo)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/items", response_model=list[MenuItemRead], summary="List menu items")
def list_menu_items(
    service: MenuService = Depends(_get_service),
) -> list[MenuItemRead]:
    """Return all items for the current tenant."""
    return list(service.list_items())


@router.post(
    "/items",
    response_model=MenuItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a menu item",
)
def create_menu_item(
    payload: MenuItemCreate,
    service: MenuService = Depends(_get_service),
) -> MenuItemRead:
    """Add a new item to the menu."""
    return service.create_item(payload)


@router.get("/items/{item_id}", response_model=MenuItemRead, summary="Get a menu item")
def get_menu_item(
    item_id: int,
    service: MenuService = Depends(_get_service),
) -> MenuItemRead:
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    return item


@router.patch("/items/{item_id}", response_model=MenuItemRead, summary="Update a menu item")
def update_menu_item(
    item_id: int,
    payload: MenuItemUpdate,
    service: MenuService = Depends(_get_service),
) -> MenuItemRead:
    item = service.update_item(item_id, payload)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a menu item")
def delete_menu_item(
    item_id: int,
    service: MenuService = Depends(_get_service),
) -> None:
    if not service.delete_item(item_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
