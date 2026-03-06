"""Domain service for the analytics-service."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from app.api.schemas import TodayStatsRead, WeeklySummaryRead
from app.infrastructure.repositories import AnalyticsRepository


class AnalyticsService:
    """Computes aggregated statistics for restaurant dashboards."""

    def __init__(self, repo: AnalyticsRepository) -> None:
        self._repo = repo

    def get_today_stats(self, restaurant_id: str) -> TodayStatsRead:
        """Return order statistics for today."""
        today = date.today()
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())

        count, revenue = self._repo.get_stats_for_period(restaurant_id, start, end)
        avg = revenue / count if count > 0 else 0.0

        return TodayStatsRead(
            restaurant_id=restaurant_id,
            date=today,
            orders_count=count,
            revenue=revenue,
            avg_order_value=round(avg, 2),
        )

    def get_weekly_summary(self, restaurant_id: str) -> WeeklySummaryRead:
        """Return aggregated statistics for the last 7 days."""
        to_date = date.today()
        from_date = to_date - timedelta(days=6)  # 7-day window inclusive
        start = datetime.combine(from_date, datetime.min.time())
        end = datetime.combine(to_date, datetime.max.time())

        count, revenue = self._repo.get_stats_for_period(restaurant_id, start, end)
        avg = revenue / count if count > 0 else 0.0

        # Find the busiest day in the breakdown
        breakdown = self._repo.get_daily_breakdown(restaurant_id, start, end)
        busiest_day = max(breakdown, key=lambda r: r[1])[0] if breakdown else None

        return WeeklySummaryRead(
            restaurant_id=restaurant_id,
            from_date=from_date,
            to_date=to_date,
            orders_count=count,
            revenue=revenue,
            avg_order_value=round(avg, 2),
            busiest_day=busiest_day,
        )
