"""ORM models for the kitchen-service."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.app.database import Base, TimestampMixin
from app.api.schemas import TicketStatus


class KitchenTicket(TimestampMixin, Base):
    """Represents a kitchen display system (KDS) ticket for an order.

    Created when an order is placed. The kitchen team uses the ticket to track
    preparation status. Each ticket maps 1:1 to an order-service ``Order``.
    """

    __tablename__ = "kitchen_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    order_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    restaurant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    table_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default=TicketStatus.NEW.value
    )

    items: Mapped[list["TicketItem"]] = relationship(
        "TicketItem", back_populates="ticket", cascade="all, delete-orphan"
    )


class TicketItem(Base):
    """A single menu item line on a kitchen ticket (no timestamps needed)."""

    __tablename__ = "ticket_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("kitchen_tickets.id", ondelete="CASCADE"), nullable=False
    )
    menu_item_id: Mapped[int] = mapped_column(Integer, nullable=False)
    menu_item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(512), nullable=True)

    ticket: Mapped["KitchenTicket"] = relationship("KitchenTicket", back_populates="items")
