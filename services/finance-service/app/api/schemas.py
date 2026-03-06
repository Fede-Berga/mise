"""Pydantic schemas for the finance-service.

Tracks financial transactions (revenue, expenses) and provides daily P&L summaries.
This is suitable for single-restaurant bookkeeping at MVP scope.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TransactionType(str, Enum):
    """Direction of a financial transaction."""

    INCOME = "INCOME"   # Revenue: e.g. table order payment
    EXPENSE = "EXPENSE" # Cost: e.g. supplier invoice, staff wage


class TransactionBase(BaseModel):
    """Core fields of a financial transaction."""

    restaurant_id: str = Field(..., max_length=64)
    transaction_type: TransactionType
    amount: float = Field(..., gt=0, description="Transaction amount in the restaurant's currency")
    description: str = Field(..., max_length=512, description="Human-readable description, e.g. 'Order #42 payment'")
    reference: str | None = Field(None, max_length=128, description="External reference, e.g. order id or invoice number")
    occurred_at: datetime | None = Field(None, description="When the transaction occurred; defaults to now")


class TransactionCreate(TransactionBase):
    """Payload for recording a new transaction."""


class TransactionRead(TransactionBase):
    """Transaction response including server-generated fields."""

    id: int
    tenant_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DailySummary(BaseModel):
    """Aggregated P&L summary for a single restaurant on a given day."""

    restaurant_id: str
    date: date
    total_income: float
    total_expense: float
    net: float = Field(description="total_income - total_expense")
    transaction_count: int
