"""Domain service layer for the restaurant-service.

Business rules live here, not in the controller or repository:
- A restaurant must have a name before it can be created.
- A table cannot be deleted if its status is OCCUPIED (guard against data loss).
- Converting ORM models to Pydantic read schemas happens here, keeping
  the controller completely free of ORM objects.

Logging: every write operation emits a structured log entry for auditability.
"""

from __future__ import annotations

import logging

from app.api.schemas import (
    RestaurantCreate,
    RestaurantRead,
    RestaurantUpdate,
    TableCreate,
    TableRead,
    TableStatus,
    TableUpdate,
)
from app.infrastructure.models import Restaurant, Table
from app.infrastructure.repositories import RestaurantRepository, TableRepository

logger = logging.getLogger(__name__)


class RestaurantService:
    """Orchestrates restaurant management operations.

    Receives repositories via constructor injection, making the service
    independently testable without a real database connection.
    """

    def __init__(self, repo: RestaurantRepository) -> None:
        self._repo = repo

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_read(restaurant: Restaurant) -> RestaurantRead:
        """Convert an ORM ``Restaurant`` instance to a Pydantic read schema."""
        return RestaurantRead.model_validate(restaurant)

    # ------------------------------------------------------------------
    # Query operations
    # ------------------------------------------------------------------

    def list_restaurants(self, *, skip: int = 0, limit: int = 50) -> list[RestaurantRead]:
        """Return a paginated list of restaurants for the current tenant."""
        return [self._to_read(r) for r in self._repo.list(skip=skip, limit=limit)]

    def get_restaurant(self, restaurant_id: int) -> RestaurantRead | None:
        """Return a single restaurant, or ``None`` if it doesn't exist."""
        restaurant = self._repo.get(restaurant_id)
        return self._to_read(restaurant) if restaurant else None

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create_restaurant(self, data: RestaurantCreate) -> RestaurantRead:
        """Create and persist a new restaurant."""
        restaurant = self._repo.create(data)
        logger.info("Restaurant created", extra={"restaurant_id": restaurant.id, "name": restaurant.name})
        return self._to_read(restaurant)

    def update_restaurant(self, restaurant_id: int, data: RestaurantUpdate) -> RestaurantRead | None:
        """Apply a partial update to a restaurant. Returns ``None`` when not found."""
        restaurant = self._repo.update(restaurant_id, data)
        if restaurant:
            logger.info("Restaurant updated", extra={"restaurant_id": restaurant_id})
        return self._to_read(restaurant) if restaurant else None

    def delete_restaurant(self, restaurant_id: int) -> bool:
        """Delete a restaurant and all its tables. Returns ``False`` when not found."""
        deleted = self._repo.delete(restaurant_id)
        if deleted:
            logger.info("Restaurant deleted", extra={"restaurant_id": restaurant_id})
        return deleted


class TableService:
    """Orchestrates table management within a restaurant."""

    def __init__(self, restaurant_repo: RestaurantRepository, table_repo: TableRepository) -> None:
        self._restaurant_repo = restaurant_repo
        self._table_repo = table_repo

    @staticmethod
    def _to_read(table: Table) -> TableRead:
        """Convert an ORM ``Table`` instance to a Pydantic read schema."""
        return TableRead.model_validate(table)

    def _assert_restaurant_exists(self, restaurant_id: int) -> None:
        """Raise ``ValueError`` if the restaurant does not exist for this tenant."""
        if not self._restaurant_repo.get(restaurant_id):
            raise ValueError(f"Restaurant {restaurant_id} not found")

    def list_tables(self, restaurant_id: int, *, skip: int = 0, limit: int = 50) -> list[TableRead]:
        """List all tables for a restaurant with pagination."""
        self._assert_restaurant_exists(restaurant_id)
        return [self._to_read(t) for t in self._table_repo.list(skip=skip, limit=limit)]

    def get_table(self, table_id: int) -> TableRead | None:
        """Return a single table, or ``None`` if not found."""
        table = self._table_repo.get(table_id)
        return self._to_read(table) if table else None

    def add_table(self, restaurant_id: int, data: TableCreate) -> TableRead:
        """Add a new table to a restaurant."""
        self._assert_restaurant_exists(restaurant_id)
        table = self._table_repo.create(data)
        logger.info("Table added", extra={"restaurant_id": restaurant_id, "table_id": table.id})
        return self._to_read(table)

    def update_table(self, table_id: int, data: TableUpdate) -> TableRead | None:
        """Partially update a table. Raises ``ValueError`` if table is OCCUPIED and being deleted."""
        table = self._table_repo.update(table_id, data)
        if table:
            logger.info("Table updated", extra={"table_id": table_id})
        return self._to_read(table) if table else None

    def remove_table(self, table_id: int) -> bool:
        """Remove a table.

        Business rule: a table with status OCCUPIED cannot be deleted — its
        active order must be closed first.
        """
        table = self._table_repo.get(table_id)
        if table and table.status == TableStatus.OCCUPIED.value:
            raise ValueError("Cannot delete an occupied table — close the active order first")
        deleted = self._table_repo.delete(table_id)
        if deleted:
            logger.info("Table removed", extra={"table_id": table_id})
        return deleted
