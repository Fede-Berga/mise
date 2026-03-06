"""HTTP controller for the analytics-service."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from common.app.database import get_db_session
from common.app.dependencies import TenantIdDep

from app.api.schemas import TodayStatsRead, WeeklySummaryRead
from app.domain.services import AnalyticsService
from app.infrastructure.repositories import AnalyticsRepository

router = APIRouter()


def _get_service(
    db: Session = Depends(get_db_session),
    tenant_id: TenantIdDep = Depends(),
) -> AnalyticsService:
    """Construct the analytics service with a tenant-scoped repository."""
    return AnalyticsService(repo=AnalyticsRepository(db=db, tenant_id=tenant_id))


@router.get("/{restaurant_id}/today", response_model=TodayStatsRead, summary="Today's stats")
def get_today_stats(
    restaurant_id: str,
    service: AnalyticsService = Depends(_get_service),
) -> TodayStatsRead:
    """Return order count, revenue, and average order value for today."""
    return service.get_today_stats(restaurant_id=restaurant_id)


@router.get("/{restaurant_id}/weekly", response_model=WeeklySummaryRead, summary="Weekly summary")
def get_weekly_summary(
    restaurant_id: str,
    service: AnalyticsService = Depends(_get_service),
) -> WeeklySummaryRead:
    """Return aggregated statistics for the past 7 days, including busiest day."""
    return service.get_weekly_summary(restaurant_id=restaurant_id)
