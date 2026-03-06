"""Domain service for the hardware-service."""

from __future__ import annotations

import logging

from app.api.schemas import (
    DeviceCreate,
    DeviceRead,
    DeviceStatus,
    DeviceUpdate,
    PingResponse,
)
from app.infrastructure.models import Device
from app.infrastructure.repositories import HardwareRepository

logger = logging.getLogger(__name__)


class HardwareService:
    """Orchestrates device registration and heartbeat tracking."""

    def __init__(self, repo: HardwareRepository) -> None:
        self._repo = repo

    @staticmethod
    def _to_read(device: Device) -> DeviceRead:
        return DeviceRead.model_validate(device)

    def list_devices(self, *, restaurant_id: str | None = None, skip: int = 0, limit: int = 50) -> list[DeviceRead]:
        """List registered devices, optionally filtered by restaurant."""
        return [self._to_read(d) for d in self._repo.list(restaurant_id=restaurant_id, skip=skip, limit=limit)]

    def get_device(self, device_id: int) -> DeviceRead | None:
        d = self._repo.get(device_id)
        return self._to_read(d) if d else None

    def register_device(self, data: DeviceCreate) -> DeviceRead:
        """Register a new hardware device (starts OFFLINE until first ping)."""
        device = self._repo.create(data)
        logger.info("Device registered", extra={"device_id": device.id, "name": device.name})
        return self._to_read(device)

    def update_device(self, device_id: int, data: DeviceUpdate) -> DeviceRead | None:
        device = self._repo.update(device_id, data)
        return self._to_read(device) if device else None

    def deregister_device(self, device_id: int) -> bool:
        """Remove a device from the registry."""
        deleted = self._repo.delete(device_id)
        if deleted:
            logger.info("Device deregistered", extra={"device_id": device_id})
        return deleted

    def ping(self, device_id: int) -> PingResponse:
        """Record a heartbeat from a device, marking it ONLINE.

        In a production implementation this could also attempt a real network
        ping (ICMP / TCP check) to the device's ip_address.
        """
        device = self._repo.record_heartbeat(device_id)
        if not device:
            return PingResponse(device_id=device_id, reachable=False, message="Device not found")
        logger.info("Device heartbeat received", extra={"device_id": device_id})
        return PingResponse(device_id=device_id, reachable=True, message="Device is online")
