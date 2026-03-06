"""ORM models for the hardware-service."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from common.app.database import Base, TimestampMixin
from app.api.schemas import DeviceStatus


class Device(TimestampMixin, Base):
    """A peripheral hardware device registered to a restaurant.

    ``last_seen_at`` is updated every time the device sends a heartbeat ping.
    The service uses it for OFFLINE detection.
    """

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    restaurant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(String(64), nullable=False)
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    mac_address: Mapped[str | None] = mapped_column(String(17), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=DeviceStatus.OFFLINE.value)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
