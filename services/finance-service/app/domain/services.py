"""Domain service for the finance-service."""

from __future__ import annotations

import logging
from datetime import date

from app.api.schemas import (
    DailySummary,
    TransactionCreate,
    TransactionRead,
    TransactionType,
)
from app.infrastructure.models import Transaction
from app.infrastructure.repositories import FinanceRepository

logger = logging.getLogger(__name__)


class FinanceService:
    """Orchestrates financial transaction recording and reporting."""

    def __init__(self, repo: FinanceRepository) -> None:
        self._repo = repo

    @staticmethod
    def _to_read(tx: Transaction) -> TransactionRead:
        return TransactionRead.model_validate(tx)

    def list_transactions(
        self,
        *,
        restaurant_id: str | None = None,
        transaction_type: TransactionType | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[TransactionRead]:
        """Return a filtered, paginated list of transactions."""
        txs = self._repo.list(
            restaurant_id=restaurant_id,
            transaction_type=transaction_type,
            from_date=from_date,
            to_date=to_date,
            skip=skip,
            limit=limit,
        )
        return [self._to_read(tx) for tx in txs]

    def get_transaction(self, transaction_id: int) -> TransactionRead | None:
        tx = self._repo.get(transaction_id)
        return self._to_read(tx) if tx else None

    def record_transaction(self, data: TransactionCreate) -> TransactionRead:
        """Record a new financial transaction."""
        tx = self._repo.create(data)
        logger.info(
            "Transaction recorded",
            extra={"tx_id": tx.id, "type": tx.transaction_type, "amount": tx.amount},
        )
        return self._to_read(tx)

    def get_daily_summary(self, restaurant_id: str, day: date) -> DailySummary:
        """Compute a daily P&L summary for a restaurant."""
        total_income, total_expense, count = self._repo.get_daily_summary(restaurant_id, day)
        return DailySummary(
            restaurant_id=restaurant_id,
            date=day,
            total_income=total_income,
            total_expense=total_expense,
            net=total_income - total_expense,
            transaction_count=count,
        )
