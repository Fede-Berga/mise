"""HTTP controller for the kitchen-service."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from common.app.database import get_db_session
from common.app.dependencies import PaginationDep, TenantIdDep

from app.api.schemas import (
    KitchenTicketCreate,
    KitchenTicketRead,
    KitchenTicketStatusUpdate,
    TicketStatus,
)
from app.domain.services import KitchenService
from app.infrastructure.repositories import KitchenRepository

router = APIRouter()


def _get_service(
    tenant_id: TenantIdDep,
    db: Session = Depends(get_db_session),
) -> KitchenService:
    """Construct the kitchen service with a tenant-scoped repository."""
    return KitchenService(repo=KitchenRepository(db=db, tenant_id=tenant_id))


@router.get("/", response_model=list[KitchenTicketRead], summary="List kitchen tickets")
def list_tickets(
    pagination: PaginationDep,
    service: KitchenService = Depends(_get_service),
    status: Optional[TicketStatus] = Query(default=None, description="Filter by ticket status"),
    restaurant_id: Optional[str] = Query(default=None, description="Filter by restaurant id"),
) -> list[KitchenTicketRead]:
    """List kitchen tickets with optional status and restaurant filters."""
    return service.list_tickets(
        status=status,
        restaurant_id=restaurant_id,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post("/", response_model=KitchenTicketRead, status_code=status.HTTP_201_CREATED, summary="Create a kitchen ticket")
def create_ticket(
    payload: KitchenTicketCreate,
    service: KitchenService = Depends(_get_service),
) -> KitchenTicketRead:
    """Create a kitchen ticket. Typically called by the order-service on order placement."""
    return service.create_ticket(payload)


@router.get("/{ticket_id}", response_model=KitchenTicketRead, summary="Get a kitchen ticket")
def get_ticket(
    ticket_id: int,
    service: KitchenService = Depends(_get_service),
) -> KitchenTicketRead:
    """Return a single kitchen ticket."""
    ticket = service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


@router.patch("/{ticket_id}/status", response_model=KitchenTicketRead, summary="Advance ticket status")
def update_ticket_status(
    ticket_id: int,
    payload: KitchenTicketStatusUpdate,
    tenant_id: TenantIdDep,
    authorization: str | None = Header(default=None, alias="Authorization"),
    service: KitchenService = Depends(_get_service),
) -> KitchenTicketRead:
    """Advance a ticket to the next lifecycle state (NEW→PREPARING→READY→DONE)."""
    try:
        ticket = service.update_status(
            ticket_id,
            payload,
            tenant_id=tenant_id,
            auth_header=authorization,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket
