"""Pydantic schemas for the hardware-service.

Manages peripheral devices (POS terminals, KDS screens, receipt printers)
connected to the restaurant network.

Extending device types: add a new value to ``DeviceType`` and handle it in
the service layer.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class DeviceType(str, Enum):
    """Category of hardware device."""

    POS_TERMINAL = "POS_TERMINAL"  # Point-of-sale touch screen
    KITCHEN_DISPLAY = "KITCHEN_DISPLAY"  # KDS screen in the kitchen
    RECEIPT_PRINTER = "RECEIPT_PRINTER"  # Thermal ticket printer
    PAYMENT_TERMINAL = "PAYMENT_TERMINAL"  # Card reader (e.g. SumUp)
    OTHER = "OTHER"


class DeviceStatus(str, Enum):
    """Operational status of a device."""

    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"


class DeviceBase(BaseModel):
    """Core fields of a hardware device."""

    name: str = Field(..., min_length=1, max_length=255, description="Human-readable name, e.g. 'Bar POS 1'")
    device_type: DeviceType
    location: str | None = Field(None, max_length=128, description="Physical location, e.g. 'Kitchen North'")
    ip_address: str | None = Field(None, max_length=45, description="IPv4 or IPv6 address on the local network")
    mac_address: str | None = Field(None, max_length=17, description="MAC address for network identification")
    restaurant_id: str = Field(..., max_length=64)


class DeviceCreate(DeviceBase):
    """Payload for registering a new device."""


class DeviceUpdate(BaseModel):
    """Partial payload for updating a device."""

    name: str | None = Field(None, min_length=1, max_length=255)
    location: str | None = None
    ip_address: str | None = None
    mac_address: str | None = None
    status: DeviceStatus | None = None


class DeviceRead(DeviceBase):
    """Device response."""

    id: int
    tenant_id: str
    status: DeviceStatus
    last_seen_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PingResponse(BaseModel):
    """Response from a device ping / heartbeat check."""

    device_id: int
    reachable: bool
    message: str
