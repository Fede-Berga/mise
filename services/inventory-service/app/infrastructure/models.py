"""ORM models for the inventory-service."""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.app.database import Base, TimestampMixin
from app.api.schemas import MovementType


class InventoryItem(TimestampMixin, Base):
    """An ingredient, raw material, or supply item tracked in the inventory.

    ``quantity_on_hand`` is updated in-place whenever a stock movement is recorded.
    Historical changes are preserved as ``StockMovement`` records.
    """

    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    quantity_on_hand: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reorder_level: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cost_per_unit: Mapped[float | None] = mapped_column(Float, nullable=True)

    movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement", back_populates="item", cascade="all, delete-orphan"
    )


class StockMovement(Base):
    """An immutable audit record for every stock quantity change.

    Stock movements are append-only — never updated or deleted. The full
    movement history provides traceability for food-cost accounting.
    """

    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    inventory_item_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False, index=True
    )
    movement_type: Mapped[str] = mapped_column(String(32), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_after: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Only created_at; movements are immutable so no updated_at needed
    from sqlalchemy import DateTime, func
    created_at: Mapped["datetime"] = mapped_column(  # type: ignore[name-defined]
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="movements")
