"""Repository layer for the analytics-service.

Queries the shared PostgreSQL database for order statistics.
Read-only — analytics never modifies data.

NOTE: For MVP we query the order-service's tables directly via the shared DB.
In production this should consume NATS events and write to ClickHouse for
separation of OLTP and OLAP concerns.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session


class AnalyticsRepository:
    """Read-only data access for order statistics, scoped to a tenant."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self._db = db
        self._tenant_id = tenant_id

    def get_stats_for_period(
        self, restaurant_id: str, start: datetime, end: datetime
    ) -> tuple[int, float]:
        """Return (orders_count, revenue) for a given restaurant in a date range."""
        stmt = text(
            """
            SELECT
                COUNT(*)              AS orders_count,
                COALESCE(SUM(total_amount), 0) AS revenue
            FROM orders
            WHERE tenant_id      = :tenant_id
              AND restaurant_id  = :restaurant_id
              AND created_at BETWEEN :start AND :end
            """
        )
        row = self._db.execute(
            stmt,
            {
                "tenant_id": self._tenant_id,
                "restaurant_id": restaurant_id,
                "start": start,
                "end": end,
            },
        ).one()
        return int(row.orders_count or 0), float(row.revenue or 0.0)

    def get_daily_breakdown(
        self, restaurant_id: str, start: datetime, end: datetime
    ) -> list[tuple[date, int, float]]:
        """Return per-day (date, orders_count, revenue) tuples for the given period."""
        stmt = text(
            """
            SELECT
                DATE(created_at)      AS day,
                COUNT(*)              AS orders_count,
                COALESCE(SUM(total_amount), 0) AS revenue
            FROM orders
            WHERE tenant_id     = :tenant_id
              AND restaurant_id = :restaurant_id
              AND created_at BETWEEN :start AND :end
            GROUP BY DATE(created_at)
            ORDER BY day
            """
        )
        rows = self._db.execute(
            stmt,
            {"tenant_id": self._tenant_id, "restaurant_id": restaurant_id, "start": start, "end": end},
        ).all()
        return [(row.day, int(row.orders_count), float(row.revenue)) for row in rows]
