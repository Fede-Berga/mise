"""Repository layer for the kitchen-service."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import KitchenTicketCreate, KitchenTicketStatusUpdate, TicketStatus
from app.infrastructure.models import KitchenTicket, TicketItem


class KitchenRepository:
    """Data access for kitchen tickets, scoped to a tenant."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self._db = db
        self._tenant_id = tenant_id

    def _base_query(self):
        return select(KitchenTicket).where(KitchenTicket.tenant_id == self._tenant_id)

    def list(
        self,
        *,
        status: TicketStatus | None = None,
        restaurant_id: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[KitchenTicket]:
        """List tickets with optional filters for status and restaurant."""
        stmt = self._base_query()
        if status:
            stmt = stmt.where(KitchenTicket.status == status.value)
        if restaurant_id:
            stmt = stmt.where(KitchenTicket.restaurant_id == restaurant_id)
        stmt = stmt.order_by(KitchenTicket.id.asc()).offset(skip).limit(limit)
        return list(self._db.execute(stmt).scalars().all())

    def get(self, ticket_id: int) -> KitchenTicket | None:
        """Fetch a single ticket by id."""
        stmt = self._base_query().where(KitchenTicket.id == ticket_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def get_by_order_id(self, order_id: int) -> KitchenTicket | None:
        """Fetch ticket by order_id for idempotency check."""
        stmt = self._base_query().where(KitchenTicket.order_id == order_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def create(self, data: KitchenTicketCreate) -> KitchenTicket:
        """Persist a new kitchen ticket with its line items."""
        ticket = KitchenTicket(
            tenant_id=self._tenant_id,
            order_id=data.order_id,
            restaurant_id=data.restaurant_id,
            table_label=data.table_label,
            status=TicketStatus.NEW.value,
        )
        self._db.add(ticket)
        self._db.flush()  # get ticket.id before creating items

        for item_data in data.items:
            self._db.add(
                TicketItem(
                    ticket_id=ticket.id,
                    menu_item_id=item_data.menu_item_id,
                    menu_item_name=item_data.menu_item_name,
                    quantity=item_data.quantity,
                    notes=item_data.notes,
                )
            )

        self._db.commit()
        self._db.refresh(ticket)
        return ticket

    def update_status(self, ticket_id: int, data: KitchenTicketStatusUpdate) -> KitchenTicket | None:
        """Advance a ticket to a new status. Returns ``None`` if not found."""
        ticket = self.get(ticket_id)
        if not ticket:
            return None
        ticket.status = data.status.value
        self._db.commit()
        self._db.refresh(ticket)
        return ticket
