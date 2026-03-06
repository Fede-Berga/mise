"""HTTP controller for the notification-service."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from common.app.database import get_db_session
from common.app.dependencies import PaginationDep, TenantIdDep

from app.api.schemas import NotificationCreate, NotificationRead
from app.domain.services import NotificationService
from app.infrastructure.repositories import NotificationRepository

router = APIRouter()


def _get_service(
    db: Session = Depends(get_db_session),
    tenant_id: TenantIdDep = Depends(),
) -> NotificationService:
    return NotificationService(repo=NotificationRepository(db=db, tenant_id=tenant_id))


@router.get("/", response_model=list[NotificationRead], summary="List notifications")
def list_notifications(
    recipient_id: Optional[str] = Query(default=None, description="Filter by recipient id"),
    pagination: PaginationDep = Depends(),
    service: NotificationService = Depends(_get_service),
) -> list[NotificationRead]:
    """Return recent notifications for this tenant (most recent first)."""
    return service.list_notifications(recipient_id=recipient_id, skip=pagination.skip, limit=pagination.limit)


@router.post("/", response_model=NotificationRead, status_code=status.HTTP_201_CREATED, summary="Send a notification")
def send_notification(payload: NotificationCreate, service: NotificationService = Depends(_get_service)) -> NotificationRead:
    """Send and log a notification to a recipient."""
    return service.send(payload)


@router.get("/{notification_id}", response_model=NotificationRead, summary="Get a notification")
def get_notification(notification_id: int, service: NotificationService = Depends(_get_service)) -> NotificationRead:
    """Return a single notification log record."""
    notification = service.get_notification(notification_id)
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notification
