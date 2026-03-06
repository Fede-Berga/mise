"""Domain service for the order-service.

Responsibilities:
1. Resolve menu item prices and names from the menu-service (HTTP call)
2. Persist the order via the repository
3. Publish ``orders.placed`` and ``orders.status_changed`` NATS events
4. Convert ORM models to Pydantic read schemas for the controller
"""

from __future__ import annotations

import json
import logging
from hashlib import sha256
from typing import Sequence

import httpx

from common.app.config import get_settings
from common.app.dragonfly import acquire_lock, cache_get_json, cache_set_json, release_lock
from common.app.events import publish_event

from app.api.schemas import (
    OrderCreate,
    OrderItemRead,
    OrderRead,
    OrderStatus,
    OrderStatusUpdate,
)
from app.infrastructure.models import Order
from app.infrastructure.repositories import OrderRepository

logger = logging.getLogger(__name__)


class OrderService:
    """Orchestrates order placement and lifecycle transitions."""

    def __init__(self, repo: OrderRepository) -> None:
        self._repo = repo

    @staticmethod
    def _to_read(order: Order) -> OrderRead:
        """Convert ORM order (with lazy-loaded items) to Pydantic read schema."""
        return OrderRead(
            id=order.id,
            tenant_id=order.tenant_id,
            restaurant_id=order.restaurant_id,
            table_id=order.table_id,
            status=OrderStatus(order.status),
            total_amount=order.total_amount,
            notes=order.notes,
            created_at=order.created_at,
            updated_at=order.updated_at,
            items=[
                OrderItemRead(
                    id=item.id,
                    menu_item_id=item.menu_item_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.line_total,
                )
                for item in order.items
            ],
        )

    @staticmethod
    def _resolve_item_details(items: list, tenant_id: str, auth_header: str | None) -> dict[int, tuple[float, str]]:
        """Resolve menu item price and name from the menu-service.

        Returns:
            dict mapping menu_item_id → (unit_price, name).
        """
        settings = get_settings()
        base_url = settings.menu_svc_url.rstrip("/")
        result: dict[int, tuple[float, str]] = {}
        headers = {"Content-Type": "application/json", "X-Tenant-Id": tenant_id}
        if auth_header:
            headers["Authorization"] = auth_header

        for item in items:
            price, name = 0.0, "Unknown"
            try:
                with httpx.Client(timeout=5.0) as client:
                    resp = client.get(
                        f"{base_url}/menus/items/{item.menu_item_id}",
                        headers=headers,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        price = float(data.get("price", 0))
                        name = str(data.get("name", "Unknown"))
            except Exception as e:
                logger.warning("Menu item %s lookup failed: %s", item.menu_item_id, e)
            result[item.menu_item_id] = (price, name)

        return result

    # ------------------------------------------------------------------
    # Query operations
    # ------------------------------------------------------------------

    def list_orders(
        self,
        *,
        status: OrderStatus | None = None,
        restaurant_id: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[OrderRead]:
        """Return a filtered, paginated list of orders."""
        orders = self._repo.list(status=status, restaurant_id=restaurant_id, skip=skip, limit=limit)
        return [self._to_read(o) for o in orders]

    def get_order(self, order_id: int) -> OrderRead | None:
        """Return a single order, or ``None`` if not found."""
        order = self._repo.get(order_id)
        return self._to_read(order) if order else None

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create_order(
        self,
        data: OrderCreate,
        tenant_id: str,
        auth_header: str | None = None,
        idempotency_key: str | None = None,
        actor_id: str | None = None,
    ) -> OrderRead:
        """Place a new order.

        Workflow:
        1. Resolve unit prices and names from the menu-service (best-effort)
        2. Persist order + line items
        3. Publish mise.orders.placed NATS event for kitchen-svc
        """
        settings = get_settings()
        canonical_payload = json.dumps(data.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        payload_hash = sha256(canonical_payload.encode("utf-8")).hexdigest()
        idempotency_cache_key = None
        idempotency_lock_key = None
        if idempotency_key:
            key_scope = f"{tenant_id}:{actor_id or 'anonymous'}:{idempotency_key}"
            idempotency_cache_key = f"idempotency:orders:create:result:{key_scope}"
            idempotency_lock_key = f"idempotency:orders:create:lock:{key_scope}"
            cached = cache_get_json(idempotency_cache_key)
            if cached:
                cached_hash = str(cached.get("payload_hash", ""))
                if cached_hash != payload_hash:
                    msg = "Idempotency-Key reused with different payload"
                    raise ValueError(msg)
                return OrderRead.model_validate(cached["response"])
            lock = acquire_lock(key=idempotency_lock_key, ttl_seconds=settings.idempotency_ttl_seconds)
            if not lock:
                msg = "A request with this Idempotency-Key is already being processed"
                raise ValueError(msg)
        else:
            lock = None

        item_details = self._resolve_item_details(data.items, tenant_id, auth_header)
        item_prices = {k: v[0] for k, v in item_details.items()}
        try:
            order = self._repo.create(data, item_prices=item_prices)

            payload = {
                "order_id": order.id,
                "tenant_id": order.tenant_id,
                "restaurant_id": order.restaurant_id,
                "table_id": order.table_id,
                "table_label": None,
                "items": [
                    {
                        "menu_item_id": item.menu_item_id,
                        "menu_item_name": item_details.get(item.menu_item_id, (0.0, "Unknown"))[1],
                        "quantity": item.quantity,
                        "notes": None,
                    }
                    for item in data.items
                ],
            }
            publish_event("mise.orders.placed", payload)
            logger.info(
                "Order placed",
                extra={"order_id": order.id, "restaurant_id": order.restaurant_id, "total": order.total_amount},
            )
            response = self._to_read(order)
            if idempotency_cache_key:
                cache_set_json(
                    idempotency_cache_key,
                    {
                        "payload_hash": payload_hash,
                        "response": response.model_dump(mode="json"),
                    },
                    ttl_seconds=settings.idempotency_ttl_seconds,
                )
            return response
        finally:
            if lock:
                release_lock(lock)

    def update_status(self, order_id: int, data: OrderStatusUpdate, tenant_id: str) -> OrderRead | None:
        """Advance an order's status. Publishes mise.orders.status_changed on success."""
        settings = get_settings()
        lock_key = f"lock:orders:status:{tenant_id}:{order_id}"
        lock = acquire_lock(key=lock_key, ttl_seconds=settings.order_status_lock_ttl_seconds)
        if not lock:
            msg = f"Order {order_id} status update already in progress"
            raise RuntimeError(msg)
        try:
            order = self._repo.get(order_id)
            old_status = order.status if order else None
            order = self._repo.update_status(order_id, data)
            if order:
                publish_event(
                    "mise.orders.status_changed",
                    {
                        "order_id": order_id,
                        "old_status": old_status,
                        "new_status": data.status.value,
                        "tenant_id": order.tenant_id,
                    },
                )
                logger.info("Order status changed", extra={"order_id": order_id, "new_status": data.status.value})
            return self._to_read(order) if order else None
        finally:
            release_lock(lock)
