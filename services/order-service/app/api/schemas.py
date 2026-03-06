"""Pydantic schemas for the order-service.

Orders are the central coordination point of the platform:
- A customer (or waiter) places an order → ``OrderCreate``
- The order moves through a lifecycle → ``OrderStatus``
- Each item in the order captures its price at the time of ordering
  (``unit_price`` snapshot) so that menu price changes do not retroactively
  alter historical orders.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(str, Enum):
    """Lifecycle status of a customer order."""

    NEW = "NEW"  # Placed, awaiting kitchen acknowledgement
    IN_PREPARATION = "IN_PREPARATION"  # Kitchen is working on it
    READY = "READY"  # Items ready for service
    CLOSED = "CLOSED"  # Delivered and paid


class OrderItemBase(BaseModel):
    """A single line item in an order."""

    menu_item_id: int = Field(..., description="Reference to the menu item")
    quantity: int = Field(..., ge=1, description="Number of portions ordered")


class OrderItemCreate(OrderItemBase):
    """Line item payload when creating an order.

    ``unit_price`` is resolved by the service from the menu-service at
    order creation time (HTTP call). Clients should not supply it.
    """


class OrderItemRead(OrderItemBase):
    """Line item response including server-generated fields."""

    id: int
    unit_price: float = Field(description="Price per unit at the time of ordering (immutable snapshot)")
    line_total: float = Field(description="unit_price × quantity")

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    """Payload for placing a new order."""

    restaurant_id: str = Field(..., max_length=64)
    table_id: int | None = Field(None, description="Optional table reference for dine-in orders")
    items: List[OrderItemCreate]
    notes: str | None = Field(None, max_length=512, description="Free-text order notes for the kitchen")


class OrderRead(BaseModel):
    """Full order response."""

    id: int
    tenant_id: str
    restaurant_id: str
    table_id: int | None
    status: OrderStatus
    total_amount: float
    notes: str | None
    items: List[OrderItemRead]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    """Payload for updating an order's status."""

    status: OrderStatus
