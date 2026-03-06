"""Pydantic schemas for the notification-service.

For the MVP, the notification service stores a log of all sent alerts and
provides endpoints to query them. The actual delivery mechanism (push, email,
SMS) is intentionally abstracted — the service logs what was sent and the
channel used.

Extending delivery channels: implement a new ``NotificationChannel`` enum
value and a corresponding sender in ``app/domain/services.py``.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class NotificationChannel(str, Enum):
    """Delivery channel for a notification."""

    IN_APP = "IN_APP"       # Stored in DB, surfaced in the web UI
    EMAIL = "EMAIL"         # Email (future: SMTP / SendGrid)
    SMS = "SMS"             # SMS (future: Twilio)
    PUSH = "PUSH"           # Mobile push (future: FCM)
    WEBHOOK = "WEBHOOK"     # HTTP callback (future)


class NotificationBase(BaseModel):
    """Core fields of a notification."""

    recipient_id: str = Field(..., max_length=128, description="User or staff member id that receives the notification")
    channel: NotificationChannel
    subject: str = Field(..., max_length=255)
    body: str = Field(..., max_length=2048)


class NotificationCreate(NotificationBase):
    """Payload for sending (and logging) a notification."""


class NotificationRead(NotificationBase):
    """Notification response."""

    id: int
    tenant_id: str
    sent_at: datetime

    model_config = ConfigDict(from_attributes=True)
