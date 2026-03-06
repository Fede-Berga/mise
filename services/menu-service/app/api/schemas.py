"""Pydantic schemas for the menu-service.

Menu items are grouped into categories (e.g. Starters, Mains, Desserts, Drinks)
to enable structured display on the restaurant's POS and web menu.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MenuItemBase(BaseModel):
    """Core fields for a menu item."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1024)
    price: float = Field(..., gt=0, description="Price in the restaurant's currency (must be positive)")
    category: str = Field("Uncategorised", max_length=100, description="Display category, e.g. 'Starters'")
    is_available: bool = Field(True, description="Whether the item is available for ordering")


class MenuItemCreate(MenuItemBase):
    """Payload for adding a new menu item."""


class MenuItemUpdate(BaseModel):
    """Partial payload for updating a menu item (PATCH semantics)."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    price: float | None = Field(None, gt=0)
    category: str | None = Field(None, max_length=100)
    is_available: bool | None = None


class MenuItemRead(MenuItemBase):
    """Menu item response including server-generated fields."""

    id: int
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
