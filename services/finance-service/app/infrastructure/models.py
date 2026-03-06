"""ORM models for the finance-service."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from common.app.database import Base


class Transaction(Base):
    """An immutable financial transaction record.

    Transactions are append-only like stock movements — never updated or deleted
    to preserve a reliable audit trail. Corrections are made via new offsetting
    transactions.
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    restaurant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # Immutable record: only created_at, no updated_at
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
