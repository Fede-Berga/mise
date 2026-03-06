"""Repository layer for the order-service.

Handles all persistence for orders and their line items.
Tenant-scoping is enforced on every query — no cross-tenant data leakage.

``unit_price`` resolution note:
For MVP, the order-service receives the unit price from an HTTP call to the
menu-service made inside the domain service layer (not here). This keeps the
repository pure database I/O with no outbound HTTP calls.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import OrderCreate, OrderStatus, OrderStatusUpdate
from app.infrastructure.models import Order, OrderItem


class OrderRepository:
    """Data access for orders, scoped to a tenant."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self._db = db
        self._tenant_id = tenant_id

    def _base_query(self):
        return select(Order).where(Order.tenant_id == self._tenant_id)

    def list(
        self,
        *,
        status: OrderStatus | None = None,
        restaurant_id: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Order]:
        """List orders with optional filters for status and restaurant."""
        stmt = self._base_query()
        if status:
            stmt = stmt.where(Order.status == status.value)
        if restaurant_id:
            stmt = stmt.where(Order.restaurant_id == restaurant_id)
        stmt = stmt.order_by(Order.id.desc()).offset(skip).limit(limit)
        return list(self._db.execute(stmt).scalars().all())

    def get(self, order_id: int) -> Order | None:
        """Fetch a single order by id."""
        stmt = self._base_query().where(Order.id == order_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def create(
        self,
        data: OrderCreate,
        item_prices: dict[int, float],  # menu_item_id → unit_price (resolved by caller)
    ) -> Order:
        """Persist a new order.

        Args:
            data:        Validated ``OrderCreate`` payload from the request.
            item_prices: Map of menu_item_id → unit_price resolved externally
                         from the menu-service. Defaults to 0.0 for unknown ids.
        """
        order = Order(
            tenant_id=self._tenant_id,
            restaurant_id=data.restaurant_id,
            table_id=data.table_id,
            status=OrderStatus.NEW.value,
            notes=data.notes,
        )
        self._db.add(order)
        self._db.flush()  # populate order.id before creating line items

        total = 0.0
        for item_data in data.items:
            unit_price = item_prices.get(item_data.menu_item_id, 0.0)
            line_total = round(unit_price * item_data.quantity, 2)
            total += line_total
            self._db.add(OrderItem(
                order_id=order.id,
                menu_item_id=item_data.menu_item_id,
                quantity=item_data.quantity,
                unit_price=unit_price,
                line_total=line_total,
            ))

        order.total_amount = round(total, 2)
        self._db.commit()
        self._db.refresh(order)
        return order

    def update_status(self, order_id: int, data: OrderStatusUpdate) -> Order | None:
        """Advance an order to a new status. Returns ``None`` if not found."""
        order = self.get(order_id)
        if not order:
            return None
        order.status = data.status.value
        self._db.commit()
        self._db.refresh(order)
        return order
