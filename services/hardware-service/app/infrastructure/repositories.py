"""Repository layer for the hardware-service."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import DeviceCreate, DeviceStatus, DeviceUpdate
from app.infrastructure.models import Device


class HardwareRepository:
    """Data access for hardware devices, tenant-scoped."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self._db = db
        self._tenant_id = tenant_id

    def _base_query(self):
        return select(Device).where(Device.tenant_id == self._tenant_id)

    def list(self, *, restaurant_id: str | None = None, skip: int = 0, limit: int = 50) -> list[Device]:
        stmt = self._base_query()
        if restaurant_id:
            stmt = stmt.where(Device.restaurant_id == restaurant_id)
        stmt = stmt.order_by(Device.name).offset(skip).limit(limit)
        return list(self._db.execute(stmt).scalars().all())

    def get(self, device_id: int) -> Device | None:
        stmt = self._base_query().where(Device.id == device_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def create(self, data: DeviceCreate) -> Device:
        device = Device(
            tenant_id=self._tenant_id,
            restaurant_id=data.restaurant_id,
            name=data.name,
            device_type=data.device_type.value,
            location=data.location,
            ip_address=data.ip_address,
            mac_address=data.mac_address,
            status=DeviceStatus.OFFLINE.value,
        )
        self._db.add(device)
        self._db.commit()
        self._db.refresh(device)
        return device

    def update(self, device_id: int, data: DeviceUpdate) -> Device | None:
        device = self.get(device_id)
        if not device:
            return None
        patch = data.model_dump(exclude_unset=True)
        if "status" in patch and patch["status"]:
            patch["status"] = patch["status"].value
        for field, value in patch.items():
            setattr(device, field, value)
        self._db.commit()
        self._db.refresh(device)
        return device

    def delete(self, device_id: int) -> bool:
        device = self.get(device_id)
        if not device:
            return False
        self._db.delete(device)
        self._db.commit()
        return True

    def record_heartbeat(self, device_id: int) -> Device | None:
        """Mark a device as ONLINE and update its last_seen_at timestamp."""
        device = self.get(device_id)
        if not device:
            return None
        device.status = DeviceStatus.ONLINE.value
        device.last_seen_at = datetime.now(tz=timezone.utc)
        self._db.commit()
        self._db.refresh(device)
        return device
