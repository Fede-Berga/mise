"""NATS consumer for kitchen-service: processes mise.orders.placed events."""

from __future__ import annotations

import logging

from app.api.schemas import KitchenTicketCreate, TicketItemCreate
from app.domain.services import KitchenService
from app.infrastructure.repositories import KitchenRepository
from common.app.database import SessionLocal

logger = logging.getLogger(__name__)


async def handle_orders_placed(payload: dict) -> None:
    """Process mise.orders.placed event: create kitchen ticket."""
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        logger.warning("mise.orders.placed missing tenant_id, skipping")
        return

    items_data = payload.get("items", [])
    if not items_data:
        logger.warning("mise.orders.placed order_id=%s has no items, skipping", payload.get("order_id"))
        return

    items = [
        TicketItemCreate(
            menu_item_id=item["menu_item_id"],
            menu_item_name=item.get("menu_item_name", "Unknown"),
            quantity=item.get("quantity", 1),
            notes=item.get("notes"),
        )
        for item in items_data
    ]
    data = KitchenTicketCreate(
        order_id=payload["order_id"],
        restaurant_id=payload["restaurant_id"],
        table_label=payload.get("table_label"),
        items=items,
    )

    db = SessionLocal()
    try:
        repo = KitchenRepository(db=db, tenant_id=tenant_id)
        service = KitchenService(repo=repo)
        service.create_ticket(data)
    except Exception as e:
        logger.exception("Failed to create kitchen ticket for order_id=%s: %s", payload.get("order_id"), e)
        raise
    finally:
        db.close()


async def handle_orders_status_changed(payload: dict) -> None:
    """Process mise.orders.status_changed event: align kitchen ticket status."""
    tenant_id = payload.get("tenant_id")
    order_id = payload.get("order_id")
    new_status = payload.get("new_status")
    if not tenant_id or order_id is None or not new_status:
        logger.warning("Invalid mise.orders.status_changed payload: %s", payload)
        return

    db = SessionLocal()
    try:
        repo = KitchenRepository(db=db, tenant_id=tenant_id)
        service = KitchenService(repo=repo)
        service.sync_ticket_from_order_status(order_id=int(order_id), order_status=str(new_status))
    except Exception as e:
        logger.exception(
            "Failed to sync kitchen ticket from order status for order_id=%s: %s",
            order_id,
            e,
        )
        raise
    finally:
        db.close()
