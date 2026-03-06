"""Repository layer for the inventory-service."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import InventoryItemCreate, InventoryItemUpdate, MovementType, StockMovementCreate
from app.infrastructure.models import InventoryItem, StockMovement


class InventoryRepository:
    """Data access for inventory items and stock movements, scoped to a tenant."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self._db = db
        self._tenant_id = tenant_id

    def _base_query(self):
        return select(InventoryItem).where(InventoryItem.tenant_id == self._tenant_id)

    # ------------------------------------------------------------------
    # Inventory items
    # ------------------------------------------------------------------

    def list_items(self, *, skip: int = 0, limit: int = 50) -> list[InventoryItem]:
        """List all inventory items for this tenant."""
        stmt = self._base_query().order_by(InventoryItem.name.asc()).offset(skip).limit(limit)
        return list(self._db.execute(stmt).scalars().all())

    def get_item(self, item_id: int) -> InventoryItem | None:
        """Fetch a single inventory item."""
        stmt = self._base_query().where(InventoryItem.id == item_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def create_item(self, data: InventoryItemCreate) -> InventoryItem:
        """Create a new inventory item."""
        item = InventoryItem(
            tenant_id=self._tenant_id,
            name=data.name,
            unit=data.unit,
            quantity_on_hand=data.quantity_on_hand,
            reorder_level=data.reorder_level,
            cost_per_unit=data.cost_per_unit,
        )
        self._db.add(item)
        self._db.commit()
        self._db.refresh(item)
        return item

    def update_item(self, item_id: int, data: InventoryItemUpdate) -> InventoryItem | None:
        """Partial update of an inventory item's metadata."""
        item = self.get_item(item_id)
        if not item:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        self._db.commit()
        self._db.refresh(item)
        return item

    def delete_item(self, item_id: int) -> bool:
        """Delete an inventory item (and its movement history via cascade)."""
        item = self.get_item(item_id)
        if not item:
            return False
        self._db.delete(item)
        self._db.commit()
        return True

    # ------------------------------------------------------------------
    # Stock movements
    # ------------------------------------------------------------------

    def record_movement(self, item_id: int, data: StockMovementCreate) -> StockMovement | None:
        """Record a stock movement and update the item's quantity_on_hand.

        OUT / WASTE movements are subtracted from stock.
        IN / ADJUSTMENT movements are added.
        Returns ``None`` if the item doesn't exist.
        """
        item = self.get_item(item_id)
        if not item:
            return None

        # Determine the signed delta
        if data.movement_type in (MovementType.OUT, MovementType.WASTE):
            delta = -data.quantity
        else:
            delta = data.quantity

        new_qty = max(0.0, item.quantity_on_hand + delta)
        movement = StockMovement(
            inventory_item_id=item_id,
            movement_type=data.movement_type.value,
            quantity=data.quantity,
            quantity_after=new_qty,
            notes=data.notes,
        )
        item.quantity_on_hand = new_qty
        self._db.add(movement)
        self._db.commit()
        self._db.refresh(movement)
        return movement

    def list_movements(self, item_id: int, *, skip: int = 0, limit: int = 100) -> list[StockMovement]:
        """Return the movement history for a single inventory item."""
        stmt = (
            select(StockMovement)
            .where(StockMovement.inventory_item_id == item_id)
            .order_by(StockMovement.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self._db.execute(stmt).scalars().all())
