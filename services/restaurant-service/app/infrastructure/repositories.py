"""Repository layer for the restaurant-service.

Repositories encapsulate all database access for their aggregate root.
They are always constructed with a ``tenant_id`` so every query is
automatically scoped to the correct tenant — no leakage is possible.

Pattern:
    repo = RestaurantRepository(db=session, tenant_id="t1")
    repo.list()              → [Restaurant, ...]
    repo.get(1)              → Restaurant | None
    repo.create(data)        → Restaurant
    repo.update(1, patch)    → Restaurant | None
    repo.delete(1)           → bool

The ``TableRepository`` follows the same pattern, scoped by ``restaurant_id``
(which is already tenant-scoped via its foreign key).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import RestaurantCreate, RestaurantUpdate, TableCreate, TableUpdate
from app.infrastructure.models import Restaurant, Table


class RestaurantRepository:
    """Data access layer for :class:`Restaurant` aggregates."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self._db = db
        self._tenant_id = tenant_id

    def _base_query(self):
        """Return a base SELECT statement pre-filtered by tenant."""
        return select(Restaurant).where(Restaurant.tenant_id == self._tenant_id)

    def list(self, *, skip: int = 0, limit: int = 50) -> list[Restaurant]:
        """List all restaurants for this tenant with pagination."""
        stmt = self._base_query().offset(skip).limit(limit)
        return list(self._db.execute(stmt).scalars().all())

    def get(self, restaurant_id: int) -> Restaurant | None:
        """Fetch a single restaurant by id, or ``None`` if not found / wrong tenant."""
        stmt = self._base_query().where(Restaurant.id == restaurant_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def create(self, data: RestaurantCreate) -> Restaurant:
        """Persist a new restaurant and return the hydrated ORM instance."""
        restaurant = Restaurant(
            tenant_id=self._tenant_id,
            name=data.name,
            address=data.address,
            phone=data.phone,
            currency=data.currency,
            timezone=data.timezone,
        )
        self._db.add(restaurant)
        self._db.commit()
        self._db.refresh(restaurant)
        return restaurant

    def update(self, restaurant_id: int, data: RestaurantUpdate) -> Restaurant | None:
        """Apply a partial update (PATCH semantics) to an existing restaurant.

        Only fields explicitly provided in ``data`` are modified.
        Returns ``None`` when the restaurant is not found.
        """
        restaurant = self.get(restaurant_id)
        if not restaurant:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(restaurant, field, value)
        self._db.commit()
        self._db.refresh(restaurant)
        return restaurant

    def delete(self, restaurant_id: int) -> bool:
        """Delete a restaurant (and its tables via cascade). Returns ``False`` if not found."""
        restaurant = self.get(restaurant_id)
        if not restaurant:
            return False
        self._db.delete(restaurant)
        self._db.commit()
        return True


class TableRepository:
    """Data access layer for :class:`Table` entities within a restaurant."""

    def __init__(self, db: Session, restaurant_id: int) -> None:
        self._db = db
        self._restaurant_id = restaurant_id

    def _base_query(self):
        """Base SELECT pre-filtered by restaurant."""
        return select(Table).where(Table.restaurant_id == self._restaurant_id)

    def list(self, *, skip: int = 0, limit: int = 50) -> list[Table]:
        """List tables for this restaurant with pagination."""
        stmt = self._base_query().offset(skip).limit(limit)
        return list(self._db.execute(stmt).scalars().all())

    def get(self, table_id: int) -> Table | None:
        """Fetch a single table or ``None``."""
        stmt = self._base_query().where(Table.id == table_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def create(self, data: TableCreate) -> Table:
        """Add a table to this restaurant."""
        table = Table(
            restaurant_id=self._restaurant_id,
            label=data.label,
            seats=data.seats,
            status=data.status.value,
        )
        self._db.add(table)
        self._db.commit()
        self._db.refresh(table)
        return table

    def update(self, table_id: int, data: TableUpdate) -> Table | None:
        """Partial update of a table. Returns ``None`` if not found."""
        table = self.get(table_id)
        if not table:
            return None
        patch = data.model_dump(exclude_unset=True)
        # Convert enum to its string value for storage
        if "status" in patch and patch["status"] is not None:
            patch["status"] = patch["status"].value
        for field, value in patch.items():
            setattr(table, field, value)
        self._db.commit()
        self._db.refresh(table)
        return table

    def delete(self, table_id: int) -> bool:
        """Remove a table. Returns ``False`` if not found."""
        table = self.get(table_id)
        if not table:
            return False
        self._db.delete(table)
        self._db.commit()
        return True
