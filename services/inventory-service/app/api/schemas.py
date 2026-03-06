"""Pydantic schemas for the inventory-service.

Tracks raw materials, ingredients, and supplies in a restaurant.
Stock movements (IN / OUT) keep a full audit trail of every quantity change.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class MovementType(str, Enum):
    """Direction of stock movement."""

    IN = "IN"   # Receiving new stock (e.g. supplier delivery)
    OUT = "OUT" # Consuming stock (e.g. ingredient used in service)
    WASTE = "WASTE"   # Spoilage / breakage
    ADJUSTMENT = "ADJUSTMENT"  # Manual correction


class InventoryItemBase(BaseModel):
    """Core fields of an inventory item."""

    name: str = Field(..., min_length=1, max_length=255, description="Name of the ingredient or supply")
    unit: str = Field(..., max_length=32, description="Unit of measure, e.g. 'kg', 'L', 'units'")
    quantity_on_hand: float = Field(0.0, ge=0, description="Current stock level")
    reorder_level: float = Field(0.0, ge=0, description="Quantity at which a reorder alert is triggered")
    cost_per_unit: float | None = Field(None, ge=0, description="Cost per unit in the restaurant's currency")


class InventoryItemCreate(InventoryItemBase):
    """Payload for adding a new inventory item."""


class InventoryItemUpdate(BaseModel):
    """Partial payload for updating an inventory item."""

    name: str | None = Field(None, min_length=1, max_length=255)
    unit: str | None = Field(None, max_length=32)
    reorder_level: float | None = Field(None, ge=0)
    cost_per_unit: float | None = Field(None, ge=0)


class InventoryItemRead(InventoryItemBase):
    """Inventory item response including server-generated fields."""

    id: int
    tenant_id: str
    low_stock: bool = Field(description="True when quantity_on_hand ≤ reorder_level")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockMovementCreate(BaseModel):
    """Payload for recording a stock movement."""

    movement_type: MovementType
    quantity: float = Field(..., gt=0, description="Quantity moved (always positive; direction set by type)")
    notes: str | None = Field(None, max_length=512, description="Reason for the movement")


class StockMovementRead(BaseModel):
    """Stock movement response."""

    id: int
    inventory_item_id: int
    movement_type: MovementType
    quantity: float
    quantity_after: float = Field(description="Stock level after this movement was applied")
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
