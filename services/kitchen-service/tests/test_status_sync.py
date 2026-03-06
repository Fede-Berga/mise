"""Unit tests for kitchen/order status synchronization flows."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace


SERVICE_APP_PATH = Path(__file__).resolve().parents[1] / "app"
COMMON_APP_PATH = Path(__file__).resolve().parents[2] / "common" / "app"
if str(SERVICE_APP_PATH.parent) not in sys.path:
    sys.path.insert(0, str(SERVICE_APP_PATH.parent))
if str(COMMON_APP_PATH.parent) not in sys.path:
    sys.path.append(str(COMMON_APP_PATH.parent))

from app.api.schemas import KitchenTicketStatusUpdate, TicketStatus  # noqa: E402
from app.domain.services import KitchenService  # noqa: E402


class _RepoStub:
    def __init__(self) -> None:
        self.ticket = SimpleNamespace(
            id=42,
            tenant_id="restaurant-0001",
            order_id=1001,
            restaurant_id="restaurant-0001",
            table_label="T1",
            status=TicketStatus.NEW.value,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            items=[],
        )
        self.updated_statuses: list[TicketStatus] = []

    def get(self, ticket_id: int):
        if ticket_id != self.ticket.id:
            return None
        return self.ticket

    def get_by_order_id(self, order_id: int):
        if order_id != self.ticket.order_id:
            return None
        return self.ticket

    def update_status(self, ticket_id: int, data: KitchenTicketStatusUpdate):
        if ticket_id != self.ticket.id:
            return None
        self.ticket.status = data.status.value
        self.updated_statuses.append(data.status)
        return self.ticket


def test_update_status_updates_ticket_and_pushes_order_status(monkeypatch):
    repo = _RepoStub()
    service = KitchenService(repo=repo)
    pushed: list[tuple[int, TicketStatus, str, str | None]] = []

    def _sync_order_status(
        *, order_id: int, ticket_status: TicketStatus, tenant_id: str, auth_header: str | None
    ) -> None:
        pushed.append((order_id, ticket_status, tenant_id, auth_header))

    monkeypatch.setattr(service, "sync_order_status", _sync_order_status)

    result = service.update_status(
        repo.ticket.id,
        KitchenTicketStatusUpdate(status=TicketStatus.PREPARING),
        tenant_id="restaurant-0001",
        auth_header="Bearer token",
    )

    assert result is not None
    assert result.status == TicketStatus.PREPARING
    assert pushed == [(repo.ticket.order_id, TicketStatus.PREPARING, "restaurant-0001", "Bearer token")]
    assert repo.updated_statuses == [TicketStatus.PREPARING]


def test_update_status_rejects_invalid_transition(monkeypatch):
    repo = _RepoStub()
    repo.ticket.status = TicketStatus.NEW.value
    service = KitchenService(repo=repo)
    called = False

    def _sync_order_status(
        *, order_id: int, ticket_status: TicketStatus, tenant_id: str, auth_header: str | None
    ) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(service, "sync_order_status", _sync_order_status)

    try:
        service.update_status(
            repo.ticket.id,
            KitchenTicketStatusUpdate(status=TicketStatus.READY),
            tenant_id="restaurant-0001",
            auth_header=None,
        )
    except ValueError as exc:
        assert "Cannot transition from NEW to READY" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid transition")

    assert called is False
    assert repo.updated_statuses == []


def test_sync_ticket_from_order_status_walks_forward_states():
    repo = _RepoStub()
    service = KitchenService(repo=repo)

    # NEW -> PREPARING -> READY
    result = service.sync_ticket_from_order_status(order_id=repo.ticket.order_id, order_status="READY")

    assert result is not None
    assert result.status == TicketStatus.READY
    assert repo.updated_statuses == [TicketStatus.READY]


def test_sync_ticket_from_order_status_maps_closed_to_done():
    repo = _RepoStub()
    repo.ticket.status = TicketStatus.PREPARING.value
    service = KitchenService(repo=repo)

    result = service.sync_ticket_from_order_status(order_id=repo.ticket.order_id, order_status="CLOSED")

    assert result is not None
    assert result.status == TicketStatus.DONE
    assert repo.updated_statuses == [TicketStatus.DONE]
