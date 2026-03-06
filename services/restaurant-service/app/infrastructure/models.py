"""SQLAlchemy ORM models for the restaurant-service.

Models:
- ``Restaurant`` — top-level entity owned by a tenant
- ``Table``      — dining tables belonging to a restaurant

Both inherit ``TimestampMixin`` so every row carries ``created_at`` /
``updated_at`` audit columns managed by the database clock.

Note on multi-tenancy: every query in the corresponding repository filters by
``tenant_id`` to enforce data isolation at the application layer. PostgreSQL
Row-Level Security (RLS) provides a second enforcement layer in production.
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.app.database import Base, TimestampMixin
from app.api.schemas import TableStatus


class Restaurant(TimestampMixin, Base):
    """A restaurant owned by a tenant.

    A single tenant may operate multiple restaurants (e.g. a franchise group).
    Each restaurant has its own set of tables, menus, and operating staff.
    """

    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(String(512), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="UTC")

    # One restaurant has many tables; deleting a restaurant also deletes its tables
    tables: Mapped[list["Table"]] = relationship(
        "Table",
        back_populates="restaurant",
        cascade="all, delete-orphan",
        lazy="select",
    )


class Table(TimestampMixin, Base):
    """A dining table within a restaurant.

    The ``status`` column tracks real-time occupancy and is updated by the
    order-service when an order is placed or closed.
    """

    __tablename__ = "tables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    restaurant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("restaurants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label: Mapped[str] = mapped_column(String(64), nullable=False)
    seats: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=TableStatus.AVAILABLE.value,
    )

    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="tables")
