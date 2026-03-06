"""Repository layer for the finance-service."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.schemas import TransactionCreate, TransactionType
from app.infrastructure.models import Transaction


class FinanceRepository:
    """Data access for financial transactions, tenant-scoped.

    Transactions are immutable once committed — this repository provides
    only append (create) and query operations.
    """

    def __init__(self, db: Session, tenant_id: str) -> None:
        self._db = db
        self._tenant_id = tenant_id

    def _base_query(self):
        return select(Transaction).where(Transaction.tenant_id == self._tenant_id)

    def list(
        self,
        *,
        restaurant_id: str | None = None,
        transaction_type: TransactionType | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Transaction]:
        """List transactions with optional multi-dimensional filters."""
        stmt = self._base_query()
        if restaurant_id:
            stmt = stmt.where(Transaction.restaurant_id == restaurant_id)
        if transaction_type:
            stmt = stmt.where(Transaction.transaction_type == transaction_type.value)
        if from_date:
            stmt = stmt.where(Transaction.occurred_at >= datetime.combine(from_date, datetime.min.time()))
        if to_date:
            stmt = stmt.where(Transaction.occurred_at <= datetime.combine(to_date, datetime.max.time()))
        stmt = stmt.order_by(Transaction.occurred_at.desc()).offset(skip).limit(limit)
        return list(self._db.execute(stmt).scalars().all())

    def get(self, transaction_id: int) -> Transaction | None:
        stmt = self._base_query().where(Transaction.id == transaction_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def create(self, data: TransactionCreate) -> Transaction:
        """Append a new immutable transaction record."""
        tx = Transaction(
            tenant_id=self._tenant_id,
            restaurant_id=data.restaurant_id,
            transaction_type=data.transaction_type.value,
            amount=data.amount,
            description=data.description,
            reference=data.reference,
            occurred_at=data.occurred_at or datetime.utcnow(),
        )
        self._db.add(tx)
        self._db.commit()
        self._db.refresh(tx)
        return tx

    def get_daily_summary(self, restaurant_id: str, day: date) -> tuple[float, float, int]:
        """Return (total_income, total_expense, count) for a given restaurant on a given day."""
        start = datetime.combine(day, datetime.min.time())
        end = datetime.combine(day, datetime.max.time())
        base = select(Transaction).where(
            Transaction.tenant_id == self._tenant_id,
            Transaction.restaurant_id == restaurant_id,
            Transaction.occurred_at >= start,
            Transaction.occurred_at <= end,
        )
        rows = list(self._db.execute(base).scalars().all())
        total_income = sum(r.amount for r in rows if r.transaction_type == TransactionType.INCOME.value)
        total_expense = sum(r.amount for r in rows if r.transaction_type == TransactionType.EXPENSE.value)
        return total_income, total_expense, len(rows)
