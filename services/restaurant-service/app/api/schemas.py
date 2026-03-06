"""Pydantic schemas for the restaurant-service.

Follows the ``Base → Create / Update → Read`` convention used across all
Mise services:
- ``*Base``   — shared field declarations
- ``*Create`` — fields required on POST (inherits Base)
- ``*Update`` — all fields optional for PATCH (partial updates)
- ``*Read``   — response model includes server-generated fields (id, timestamps)
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TableStatus(str, Enum):
    """Lifecycle status of a dining table."""

    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    CLOSED = "CLOSED"  # e.g. temporarily removed from service


# ---------------------------------------------------------------------------
# Restaurant schemas
# ---------------------------------------------------------------------------


class RestaurantBase(BaseModel):
    """Fields shared between create and read for a restaurant."""

    name: str = Field(..., min_length=1, max_length=255, description="Display name of the restaurant")
    address: str | None = Field(None, max_length=512, description="Physical address")
    phone: str | None = Field(None, max_length=50, description="Contact phone number")
    currency: str = Field("EUR", max_length=3, description="ISO 4217 currency code, e.g. EUR, USD")
    timezone: str = Field("UTC", max_length=64, description="IANA timezone, e.g. Europe/Rome")


class RestaurantCreate(RestaurantBase):
    """Payload for creating a new restaurant."""


class RestaurantUpdate(BaseModel):
    """Partial payload for updating a restaurant. All fields are optional."""

    name: str | None = Field(None, min_length=1, max_length=255)
    address: str | None = None
    phone: str | None = None
    currency: str | None = Field(None, max_length=3)
    timezone: str | None = Field(None, max_length=64)


class RestaurantRead(RestaurantBase):
    """Restaurant response model including server-generated fields."""

    id: int
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Table schemas
# ---------------------------------------------------------------------------


class TableBase(BaseModel):
    """Fields shared between create and read for a table."""

    label: str = Field(..., min_length=1, max_length=64, description="Table label, e.g. 'T-01', 'Bar 3'")
    seats: int = Field(..., ge=1, le=100, description="Number of seats at this table")
    status: TableStatus = Field(TableStatus.AVAILABLE, description="Current operational status")


class TableCreate(TableBase):
    """Payload for adding a table to a restaurant."""


class TableUpdate(BaseModel):
    """Partial payload for updating a table."""

    label: str | None = Field(None, min_length=1, max_length=64)
    seats: int | None = Field(None, ge=1, le=100)
    status: TableStatus | None = None


class TableRead(TableBase):
    """Table response model including server-generated fields."""

    id: int
    restaurant_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
