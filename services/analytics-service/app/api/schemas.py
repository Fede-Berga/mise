"""Pydantic schemas for the analytics-service.

Provides aggregated statistics over order data for restaurant dashboards.

Note on data architecture:
For the MVP, analytics data is queried directly from the shared PostgreSQL
instance. In a later iteration this should move to a dedicated OLAP store
(e.g. ClickHouse) fed by NATS events — keeping analytics workloads separate
from OLTP workloads.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class TodayStatsRead(BaseModel):
    """Daily statistics for a restaurant (aggregated today)."""

    restaurant_id: str
    date: date
    orders_count: int
    revenue: float
    avg_order_value: float = Field(description="Average order value; 0 if no orders")


class WeeklySummaryRead(BaseModel):
    """Aggregated statistics for the last 7 days for a restaurant."""

    restaurant_id: str
    from_date: date
    to_date: date
    orders_count: int
    revenue: float
    avg_order_value: float
    busiest_day: date | None = Field(None, description="Day with the highest order count in the period")
