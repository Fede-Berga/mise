"""HTTP controller for the finance-service."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from common.app.database import get_db_session
from common.app.dependencies import PaginationDep, TenantIdDep

from app.api.schemas import (
    DailySummary,
    TransactionCreate,
    TransactionRead,
    TransactionType,
)
from app.domain.services import FinanceService
from app.infrastructure.repositories import FinanceRepository

router = APIRouter()


def _get_service(
    db: Session = Depends(get_db_session),
    tenant_id: TenantIdDep = Depends(),
) -> FinanceService:
    return FinanceService(repo=FinanceRepository(db=db, tenant_id=tenant_id))


@router.get("/transactions/", response_model=list[TransactionRead], summary="List transactions")
def list_transactions(
    restaurant_id: Optional[str] = Query(default=None),
    transaction_type: Optional[TransactionType] = Query(default=None),
    from_date: Optional[date] = Query(default=None, description="Start date (inclusive), e.g. 2025-01-01"),
    to_date: Optional[date] = Query(default=None, description="End date (inclusive), e.g. 2025-01-31"),
    pagination: PaginationDep = Depends(),
    service: FinanceService = Depends(_get_service),
) -> list[TransactionRead]:
    """Return a filtered, paginated list of financial transactions."""
    return service.list_transactions(
        restaurant_id=restaurant_id,
        transaction_type=transaction_type,
        from_date=from_date,
        to_date=to_date,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post(
    "/transactions/",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Record a transaction",
)
def record_transaction(payload: TransactionCreate, service: FinanceService = Depends(_get_service)) -> TransactionRead:
    """Record a new financial transaction (income or expense)."""
    return service.record_transaction(payload)


@router.get("/transactions/{transaction_id}", response_model=TransactionRead, summary="Get a transaction")
def get_transaction(transaction_id: int, service: FinanceService = Depends(_get_service)) -> TransactionRead:
    """Return a single transaction by id."""
    tx = service.get_transaction(transaction_id)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return tx


@router.get("/summary/daily", response_model=DailySummary, summary="Daily P&L summary")
def daily_summary(
    restaurant_id: str = Query(..., description="Restaurant id to summarise"),
    day: date = Query(default_factory=date.today, description="Date to summarise (defaults to today)"),
    service: FinanceService = Depends(_get_service),
) -> DailySummary:
    """Return income, expense, and net P&L for a restaurant on a given day."""
    return service.get_daily_summary(restaurant_id, day)
