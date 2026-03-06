"""SQLAlchemy ORM models for the order-service.

Order lifecycle:
    NEW → IN_PREPARATION → READY → CLOSED

``OrderItem.unit_price`` is a snapshot of the menu item's price at the moment
the order was placed. This decouples the order history from menu price changes.
``OrderItem.line_total`` is a stored computed column (quantity × unit_price)
to avoid recalculating on every read.
"""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.app.database import Base, TimestampMixin
from app.api.schemas import OrderStatus


class Order(TimestampMixin, Base):
    """A customer order within a tenant's restaurant."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    restaurant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    table_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=OrderStatus.NEW.value)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """A single menu item line within an order.

    ``unit_price`` is a denormalized snapshot — storing it here guarantees
    that historical order totals remain correct even when menu prices change.
    """

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    menu_item_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    line_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
