"""Domain service for the inventory-service."""

from __future__ import annotations

import logging

from app.api.schemas import (
    InventoryItemCreate,
    InventoryItemRead,
    InventoryItemUpdate,
    StockMovementCreate,
    StockMovementRead,
)
from app.infrastructure.models import InventoryItem, StockMovement
from app.infrastructure.repositories import InventoryRepository

logger = logging.getLogger(__name__)


class InventoryService:
    """Orchestrates inventory item management and stock movements."""

    def __init__(self, repo: InventoryRepository) -> None:
        self._repo = repo

    @staticmethod
    def _item_to_read(item: InventoryItem) -> InventoryItemRead:
        """Convert ORM item to Pydantic read schema, computing the ``low_stock`` flag."""
        return InventoryItemRead(
            id=item.id,
            tenant_id=item.tenant_id,
            name=item.name,
            unit=item.unit,
            quantity_on_hand=item.quantity_on_hand,
            reorder_level=item.reorder_level,
            cost_per_unit=item.cost_per_unit,
            low_stock=item.quantity_on_hand <= item.reorder_level,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )

    @staticmethod
    def _movement_to_read(movement: StockMovement) -> StockMovementRead:
        """Convert ORM stock movement to Pydantic read schema."""
        return StockMovementRead.model_validate(movement)

    # ------------------------------------------------------------------
    # Item operations
    # ------------------------------------------------------------------

    def list_items(self, *, skip: int = 0, limit: int = 50) -> list[InventoryItemRead]:
        """Return a paginated list of inventory items."""
        return [self._item_to_read(i) for i in self._repo.list_items(skip=skip, limit=limit)]

    def get_item(self, item_id: int) -> InventoryItemRead | None:
        """Return a single inventory item or ``None``."""
        item = self._repo.get_item(item_id)
        return self._item_to_read(item) if item else None

    def create_item(self, data: InventoryItemCreate) -> InventoryItemRead:
        """Create and persist a new inventory item."""
        item = self._repo.create_item(data)
        logger.info("Inventory item created", extra={"item_id": item.id, "name": item.name})
        return self._item_to_read(item)

    def update_item(self, item_id: int, data: InventoryItemUpdate) -> InventoryItemRead | None:
        """Partially update an inventory item."""
        item = self._repo.update_item(item_id, data)
        return self._item_to_read(item) if item else None

    def delete_item(self, item_id: int) -> bool:
        """Delete an inventory item and its movement history."""
        return self._repo.delete_item(item_id)

    # ------------------------------------------------------------------
    # Stock movement operations
    # ------------------------------------------------------------------

    def record_movement(self, item_id: int, data: StockMovementCreate) -> StockMovementRead | None:
        """Record a stock movement (IN, OUT, WASTE, ADJUSTMENT).

        Raises:
            ValueError: if the item does not exist for this tenant.
        """
        movement = self._repo.record_movement(item_id, data)
        if movement is None:
            raise ValueError(f"Inventory item {item_id} not found")
        logger.info(
            "Stock movement recorded",
            extra={"item_id": item_id, "type": data.movement_type.value, "qty": data.quantity},
        )
        return self._movement_to_read(movement)

    def list_movements(self, item_id: int, *, skip: int = 0, limit: int = 100) -> list[StockMovementRead]:
        """Return the movement history for an inventory item (most recent first)."""
        if not self._repo.get_item(item_id):
            raise ValueError(f"Inventory item {item_id} not found")
        return [self._movement_to_read(m) for m in self._repo.list_movements(item_id, skip=skip, limit=limit)]
