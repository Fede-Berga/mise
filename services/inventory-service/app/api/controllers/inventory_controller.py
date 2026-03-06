"""HTTP controller for the inventory-service."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from common.app.database import get_db_session
from common.app.dependencies import PaginationDep, TenantIdDep

from app.api.schemas import (
    InventoryItemCreate,
    InventoryItemRead,
    InventoryItemUpdate,
    StockMovementCreate,
    StockMovementRead,
)
from app.domain.services import InventoryService
from app.infrastructure.repositories import InventoryRepository

router = APIRouter()


def _get_service(
    db: Session = Depends(get_db_session),
    tenant_id: TenantIdDep = Depends(),
) -> InventoryService:
    """Construct the inventory service with a tenant-scoped repository."""
    return InventoryService(repo=InventoryRepository(db=db, tenant_id=tenant_id))


@router.get("/", response_model=list[InventoryItemRead], summary="List inventory items")
def list_items(
    pagination: PaginationDep,
    service: InventoryService = Depends(_get_service),
) -> list[InventoryItemRead]:
    """Return all inventory items for this tenant (paginated, sorted by name)."""
    return service.list_items(skip=pagination.skip, limit=pagination.limit)


@router.post("/", response_model=InventoryItemRead, status_code=status.HTTP_201_CREATED, summary="Create inventory item")
def create_item(
    payload: InventoryItemCreate,
    service: InventoryService = Depends(_get_service),
) -> InventoryItemRead:
    """Add a new ingredient, supply, or raw material to the inventory."""
    return service.create_item(payload)


@router.get("/{item_id}", response_model=InventoryItemRead, summary="Get inventory item")
def get_item(
    item_id: int,
    service: InventoryService = Depends(_get_service),
) -> InventoryItemRead:
    """Return a single inventory item."""
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return item


@router.patch("/{item_id}", response_model=InventoryItemRead, summary="Update inventory item")
def update_item(
    item_id: int,
    payload: InventoryItemUpdate,
    service: InventoryService = Depends(_get_service),
) -> InventoryItemRead:
    """Partially update an inventory item's metadata (name, unit, reorder level)."""
    item = service.update_item(item_id, payload)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete inventory item")
def delete_item(
    item_id: int,
    service: InventoryService = Depends(_get_service),
) -> None:
    """Delete an inventory item and its full movement history."""
    if not service.delete_item(item_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")


@router.post("/{item_id}/movements", response_model=StockMovementRead, status_code=status.HTTP_201_CREATED, summary="Record stock movement")
def record_movement(
    item_id: int,
    payload: StockMovementCreate,
    service: InventoryService = Depends(_get_service),
) -> StockMovementRead:
    """Record a stock movement (IN, OUT, WASTE, ADJUSTMENT) for an inventory item."""
    try:
        return service.record_movement(item_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{item_id}/movements", response_model=list[StockMovementRead], summary="List stock movements")
def list_movements(
    item_id: int,
    pagination: PaginationDep,
    service: InventoryService = Depends(_get_service),
) -> list[StockMovementRead]:
    """Return the movement history for an inventory item (most recent first)."""
    try:
        return service.list_movements(item_id, skip=pagination.skip, limit=pagination.limit)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
