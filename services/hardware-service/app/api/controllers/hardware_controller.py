"""HTTP controller for the hardware-service."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from common.app.database import get_db_session
from common.app.dependencies import PaginationDep, TenantIdDep

from app.api.schemas import DeviceCreate, DeviceRead, DeviceUpdate, PingResponse
from app.domain.services import HardwareService
from app.infrastructure.repositories import HardwareRepository

router = APIRouter()


def _get_service(
    db: Session = Depends(get_db_session),
    tenant_id: TenantIdDep = Depends(),
) -> HardwareService:
    return HardwareService(repo=HardwareRepository(db=db, tenant_id=tenant_id))


@router.get("/", response_model=list[DeviceRead], summary="List devices")
def list_devices(
    restaurant_id: Optional[str] = Query(default=None, description="Filter by restaurant id"),
    pagination: PaginationDep = Depends(),
    service: HardwareService = Depends(_get_service),
) -> list[DeviceRead]:
    """List all registered hardware devices."""
    return service.list_devices(restaurant_id=restaurant_id, skip=pagination.skip, limit=pagination.limit)


@router.post("/", response_model=DeviceRead, status_code=status.HTTP_201_CREATED, summary="Register a device")
def register_device(payload: DeviceCreate, service: HardwareService = Depends(_get_service)) -> DeviceRead:
    """Register a new hardware device. Device starts in OFFLINE status until first ping."""
    return service.register_device(payload)


@router.get("/{device_id}", response_model=DeviceRead, summary="Get a device")
def get_device(device_id: int, service: HardwareService = Depends(_get_service)) -> DeviceRead:
    """Return a single device."""
    device = service.get_device(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.patch("/{device_id}", response_model=DeviceRead, summary="Update a device")
def update_device(
    device_id: int, payload: DeviceUpdate, service: HardwareService = Depends(_get_service)
) -> DeviceRead:
    """Partially update device metadata (name, location, status)."""
    device = service.update_device(device_id, payload)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deregister a device")
def deregister_device(device_id: int, service: HardwareService = Depends(_get_service)) -> None:
    """Remove a device from the registry."""
    if not service.deregister_device(device_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")


@router.post("/{device_id}/ping", response_model=PingResponse, summary="Ping / heartbeat")
def ping_device(device_id: int, service: HardwareService = Depends(_get_service)) -> PingResponse:
    """Record a heartbeat from a device, marking it ONLINE and updating last_seen_at."""
    return service.ping(device_id)
