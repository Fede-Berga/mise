"""Domain service for the kitchen-service.

Business rules:
- Ticket status can only advance forward in its lifecycle:
  NEW → PREPARING → READY → DONE. Reverting is not allowed.
- A ticket cannot be created for an order_id that already has a ticket
  (idempotency guard using order_id uniqueness check).
"""

from __future__ import annotations

import logging

import httpx

from common.app.config import get_settings

from app.api.schemas import (
    KitchenTicketCreate,
    KitchenTicketRead,
    KitchenTicketStatusUpdate,
    TicketItemRead,
    TicketStatus,
)
from app.infrastructure.models import KitchenTicket
from app.infrastructure.repositories import KitchenRepository

logger = logging.getLogger(__name__)

# Defines the only valid forward transitions
_VALID_TRANSITIONS: dict[TicketStatus, set[TicketStatus]] = {
    TicketStatus.NEW: {TicketStatus.PREPARING},
    TicketStatus.PREPARING: {TicketStatus.READY},
    TicketStatus.READY: {TicketStatus.DONE},
    TicketStatus.DONE: set(),  # terminal state
}

_ORDER_TO_TICKET_STATUS: dict[str, TicketStatus] = {
    "NEW": TicketStatus.NEW,
    "IN_PREPARATION": TicketStatus.PREPARING,
    "READY": TicketStatus.READY,
    "CLOSED": TicketStatus.DONE,
}

_TICKET_TO_ORDER_STATUS: dict[TicketStatus, str] = {
    TicketStatus.NEW: "NEW",
    TicketStatus.PREPARING: "IN_PREPARATION",
    TicketStatus.READY: "READY",
    TicketStatus.DONE: "CLOSED",
}


class KitchenService:
    """Orchestrates kitchen ticket operations."""

    def __init__(self, repo: KitchenRepository) -> None:
        self._repo = repo

    @staticmethod
    def _to_read(ticket: KitchenTicket) -> KitchenTicketRead:
        """Convert ORM ticket to Pydantic read schema."""
        return KitchenTicketRead(
            id=ticket.id,
            tenant_id=ticket.tenant_id,
            order_id=ticket.order_id,
            restaurant_id=ticket.restaurant_id,
            table_label=ticket.table_label,
            status=TicketStatus(ticket.status),
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            items=[
                TicketItemRead(
                    id=i.id,
                    menu_item_id=i.menu_item_id,
                    menu_item_name=i.menu_item_name,
                    quantity=i.quantity,
                    notes=i.notes,
                )
                for i in ticket.items
            ],
        )

    def list_tickets(
        self,
        *,
        status: TicketStatus | None = None,
        restaurant_id: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[KitchenTicketRead]:
        """Return tickets filtered by optional status and restaurant."""
        tickets = self._repo.list(status=status, restaurant_id=restaurant_id, skip=skip, limit=limit)
        return [self._to_read(t) for t in tickets]

    def get_ticket(self, ticket_id: int) -> KitchenTicketRead | None:
        """Return a single ticket or ``None``."""
        ticket = self._repo.get(ticket_id)
        return self._to_read(ticket) if ticket else None

    def create_ticket(self, data: KitchenTicketCreate) -> KitchenTicketRead | None:
        """Create a kitchen ticket from an incoming order. Returns None if already exists (idempotency)."""
        existing = self._repo.get_by_order_id(data.order_id)
        if existing:
            logger.debug("Ticket already exists for order_id=%s, skipping", data.order_id)
            return self._to_read(existing)
        ticket = self._repo.create(data)
        logger.info("Kitchen ticket created", extra={"ticket_id": ticket.id, "order_id": data.order_id})
        return self._to_read(ticket)

    def update_status(
        self,
        ticket_id: int,
        data: KitchenTicketStatusUpdate,
        *,
        tenant_id: str,
        auth_header: str | None,
    ) -> KitchenTicketRead | None:
        """Advance a ticket to the next allowed status.

        Raises:
            ValueError: if the requested transition is not valid.
        """
        ticket = self._repo.get(ticket_id)
        if not ticket:
            return None

        current = TicketStatus(ticket.status)
        if data.status not in _VALID_TRANSITIONS[current]:
            allowed = ", ".join(s.value for s in _VALID_TRANSITIONS[current]) or "none (terminal state)"
            raise ValueError(
                f"Cannot transition from {current.value} to {data.status.value}. Allowed next states: {allowed}"
            )

        # Keep order-service and kitchen-service statuses aligned.
        self.sync_order_status(
            order_id=ticket.order_id,
            ticket_status=data.status,
            tenant_id=tenant_id,
            auth_header=auth_header,
        )

        updated = self._repo.update_status(ticket_id, data)
        if updated:
            logger.info(
                "Ticket status updated",
                extra={"ticket_id": ticket_id, "new_status": data.status.value},
            )
        return self._to_read(updated) if updated else None

    def sync_ticket_from_order_status(self, order_id: int, order_status: str) -> KitchenTicketRead | None:
        """Align a kitchen ticket status with an order-service status event."""
        ticket = self._repo.get_by_order_id(order_id)
        if not ticket:
            logger.debug("No ticket found for order_id=%s when syncing from order status", order_id)
            return None

        target = _ORDER_TO_TICKET_STATUS.get(order_status)
        if target is None:
            logger.warning("Unknown order status %s for order_id=%s", order_status, order_id)
            return self._to_read(ticket)

        current = TicketStatus(ticket.status)
        if current == target:
            return self._to_read(ticket)

        # Move forward through valid transitions to reach target status.
        while current != target:
            next_states = _VALID_TRANSITIONS[current]
            if target in next_states:
                current = target
            elif len(next_states) == 1:
                current = next(iter(next_states))
            else:
                logger.warning(
                    "Cannot align ticket_id=%s from %s to %s",
                    ticket.id,
                    current.value,
                    target.value,
                )
                return self._to_read(ticket)

        updated = self._repo.update_status(ticket.id, KitchenTicketStatusUpdate(status=current))
        return self._to_read(updated) if updated else None

    def sync_order_status(
        self,
        *,
        order_id: int,
        ticket_status: TicketStatus,
        tenant_id: str,
        auth_header: str | None,
    ) -> None:
        """Push ticket status to order-service."""
        settings = get_settings()
        base_url = settings.order_svc_url.rstrip("/")
        order_status = _TICKET_TO_ORDER_STATUS[ticket_status]
        headers = {"Content-Type": "application/json", "X-Tenant-Id": tenant_id}
        if auth_header:
            headers["Authorization"] = auth_header

        with httpx.Client(timeout=5.0) as client:
            response = client.patch(
                f"{base_url}/orders/{order_id}/status",
                headers=headers,
                json={"status": order_status},
            )
            if response.status_code >= 400:
                raise RuntimeError(f"Failed to sync order status: HTTP {response.status_code}")
