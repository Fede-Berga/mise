"""Pydantic schemas for the kitchen-service.

Kitchen tickets mirror orders from the order-service. They represent the
kitchen display system (KDS) view of work to be done.

Ticket lifecycle:
    NEW → PREPARING → READY → DONE
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TicketStatus(str, Enum):
    """Lifecycle status of a kitchen ticket."""

    NEW = "NEW"             # Just received, not yet acknowledged
    PREPARING = "PREPARING" # Cook has started preparing
    READY = "READY"         # Dishes ready for pick-up / delivery
    DONE = "DONE"           # Delivered to the table / closed


class TicketItemBase(BaseModel):
    """A single line item on a kitchen ticket."""

    menu_item_id: int = Field(..., description="Reference to the menu item being prepared")
    menu_item_name: str = Field(..., max_length=255, description="Snapshot of the item name at order time")
    quantity: int = Field(..., ge=1, description="Number of portions to prepare")
    notes: str | None = Field(None, max_length=512, description="Preparation notes, e.g. 'no onions'")


class TicketItemCreate(TicketItemBase):
    """Line item payload when creating a ticket."""


class TicketItemRead(TicketItemBase):
    """Line item response including server-generated id."""

    id: int
    model_config = ConfigDict(from_attributes=True)


class KitchenTicketBase(BaseModel):
    """Core fields of a kitchen ticket."""

    order_id: int = Field(..., description="The order-service order id this ticket corresponds to")
    restaurant_id: str = Field(..., max_length=64, description="Owning restaurant id")
    table_label: str | None = Field(None, max_length=64, description="Table label for context on the KDS screen")


class KitchenTicketCreate(KitchenTicketBase):
    """Payload for creating a kitchen ticket (called by order-service on order placement)."""

    items: list[TicketItemCreate]


class KitchenTicketStatusUpdate(BaseModel):
    """Payload for advancing a ticket through its lifecycle."""

    status: TicketStatus


class KitchenTicketRead(KitchenTicketBase):
    """Full kitchen ticket response."""

    id: int
    tenant_id: str
    status: TicketStatus
    items: list[TicketItemRead]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
