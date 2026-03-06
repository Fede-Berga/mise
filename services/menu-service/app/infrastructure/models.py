"""SQLAlchemy ORM models for the menu-service."""

from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from common.app.database import Base, TimestampMixin


class MenuItem(TimestampMixin, Base):
    """A dish or beverage offered on a restaurant menu.

    Items are tenant-scoped and can be toggled available/unavailable
    without deletion to preserve order history references.
    """

    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="Uncategorised")
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
