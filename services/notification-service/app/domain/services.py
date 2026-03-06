"""Domain service for the notification-service."""

from __future__ import annotations

import logging

from app.api.schemas import NotificationChannel, NotificationCreate, NotificationRead
from app.infrastructure.models import Notification
from app.infrastructure.repositories import NotificationRepository

logger = logging.getLogger(__name__)


class NotificationService:
    """Orchestrates notification delivery and logging.

    MVP behaviour: all channels are logged to the database. Actual delivery
    (email, push, SMS) is a future extension — add a sender per channel in
    ``_deliver``.
    """

    def __init__(self, repo: NotificationRepository) -> None:
        self._repo = repo

    @staticmethod
    def _to_read(notification: Notification) -> NotificationRead:
        return NotificationRead.model_validate(notification)

    def list_notifications(
        self,
        *,
        recipient_id: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[NotificationRead]:
        """List recent notifications for this tenant."""
        return [self._to_read(n) for n in self._repo.list(recipient_id=recipient_id, skip=skip, limit=limit)]

    def get_notification(self, notification_id: int) -> NotificationRead | None:
        n = self._repo.get(notification_id)
        return self._to_read(n) if n else None

    def send(self, data: NotificationCreate) -> NotificationRead:
        """Log and (in future) deliver a notification.

        Extension point: add channel-specific senders here, e.g.:
            if data.channel == NotificationChannel.EMAIL:
                email_sender.send(data.recipient_id, data.subject, data.body)
        """
        # Log always, regardless of channel
        notification = self._repo.create(data)
        logger.info(
            "Notification sent",
            extra={"notification_id": notification.id, "channel": data.channel.value, "recipient": data.recipient_id},
        )
        return self._to_read(notification)
