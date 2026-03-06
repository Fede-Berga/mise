"""Tests for order-service Dragonfly-backed resilience features."""

from __future__ import annotations

import json
import sys
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest

SERVICE_APP_PATH = Path(__file__).resolve().parents[1] / "app"
COMMON_APP_PATH = Path(__file__).resolve().parents[2] / "common" / "app"
if str(SERVICE_APP_PATH.parent) not in sys.path:
    sys.path.insert(0, str(SERVICE_APP_PATH.parent))
if str(COMMON_APP_PATH.parent) not in sys.path:
    sys.path.append(str(COMMON_APP_PATH.parent))

from app.api.schemas import OrderCreate, OrderItemCreate, OrderRead, OrderStatus, OrderStatusUpdate  # noqa: E402
from app.domain.services import OrderService  # noqa: E402


def _payload_hash(payload: OrderCreate) -> str:
    canonical = json.dumps(payload.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def test_create_order_returns_cached_response_when_idempotency_hit(monkeypatch):
    payload = OrderCreate(
        restaurant_id="restaurant-0001",
        table_id=1,
        items=[OrderItemCreate(menu_item_id=1, quantity=2)],
        notes="no onions",
    )
    expected = OrderRead(
        id=123,
        tenant_id="restaurant-0001",
        restaurant_id="restaurant-0001",
        table_id=1,
        status=OrderStatus.NEW,
        total_amount=25.0,
        notes="no onions",
        items=[],
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
    )
    cache_doc = {
        "payload_hash": _payload_hash(payload),
        "response": expected.model_dump(mode="json"),
    }
    monkeypatch.setattr("app.domain.services.cache_get_json", lambda _key: cache_doc)

    class _RepoStub:
        def create(self, *_args, **_kwargs):
            raise AssertionError("Repository create must not be called on cache hit")

    service = OrderService(repo=_RepoStub())
    result = service.create_order(
        payload,
        tenant_id="restaurant-0001",
        auth_header="Bearer token",
        idempotency_key="idem-1",
        actor_id="user-1",
    )
    assert result.id == 123
    assert result.total_amount == 25.0


def test_update_status_raises_when_lock_not_acquired(monkeypatch):
    monkeypatch.setattr("app.domain.services.acquire_lock", lambda **_kwargs: None)
    service = OrderService(repo=SimpleNamespace())

    with pytest.raises(RuntimeError) as exc:
        service.update_status(
            10,
            OrderStatusUpdate(status=OrderStatus.READY),
            tenant_id="restaurant-0001",
        )

    assert "already in progress" in str(exc.value)
