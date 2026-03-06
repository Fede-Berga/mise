"""Repository layer for the notification-service."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import NotificationCreate
from app.infrastructure.models import Notification


class NotificationRepository:
    """Data access for notification records, tenant-scoped."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self._db = db
        self._tenant_id = tenant_id

    def list(self, *, recipient_id: str | None = None, skip: int = 0, limit: int = 50) -> list[Notification]:
        """List recent notifications, optionally filtered by recipient."""
        stmt = select(Notification).where(Notification.tenant_id == self._tenant_id)
        if recipient_id:
            stmt = stmt.where(Notification.recipient_id == recipient_id)
        stmt = stmt.order_by(Notification.id.desc()).offset(skip).limit(limit)
        return list(self._db.execute(stmt).scalars().all())

    def get(self, notification_id: int) -> Notification | None:
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.tenant_id == self._tenant_id,
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def create(self, data: NotificationCreate) -> Notification:
        """Log a new notification record."""
        notification = Notification(
            tenant_id=self._tenant_id,
            recipient_id=data.recipient_id,
            channel=data.channel.value,
            subject=data.subject,
            body=data.body,
        )
        self._db.add(notification)
        self._db.commit()
        self._db.refresh(notification)
        return notification
