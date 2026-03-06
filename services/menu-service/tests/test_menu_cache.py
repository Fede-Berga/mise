"""Tests for menu-service Dragonfly cache integration."""

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
    sys.path.insert(0, str(COMMON_APP_PATH.parent))

from app.api.schemas import MenuItemCreate  # noqa: E402
from app.domain.services import MenuService  # noqa: E402


def test_list_items_uses_cache_when_available(monkeypatch):
    cached = [
        {
            "id": 1,
            "tenant_id": "restaurant-0001",
            "name": "Espresso",
            "description": "Single shot",
            "price": 2.5,
            "category": "Drinks",
            "is_available": True,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        },
    ]
    monkeypatch.setattr("app.domain.services.cache_get_json", lambda _key: cached)

    class _RepoStub:
        tenant_id = "restaurant-0001"

        def list_items(self):
            raise AssertionError("Repo must not be called when cache is hit")

    service = MenuService(repo=_RepoStub())
    items = service.list_items()
    assert len(items) == 1
    assert items[0].name == "Espresso"


def test_create_item_invalidates_list_and_item_cache(monkeypatch):
    deleted: list[str] = []
    monkeypatch.setattr("app.domain.services.cache_delete", lambda *keys: deleted.extend(keys))

    now = datetime.now(tz=UTC)

    class _RepoStub:
        tenant_id = "restaurant-0001"

        def create_item(self, _data):
            return SimpleNamespace(
                id=7,
                tenant_id="restaurant-0001",
                name="Tiramisu",
                description="Classic",
                price=7.0,
                category="Desserts",
                is_available=True,
                created_at=now,
                updated_at=now,
            )

    service = MenuService(repo=_RepoStub())
    created = service.create_item(
        MenuItemCreate(
            name="Tiramisu",
            description="Classic",
            price=7.0,
            category="Desserts",
            is_available=True,
        )
    )
    assert created.id == 7
    assert "cache:menu:restaurant-0001:items" in deleted
    assert "cache:menu:restaurant-0001:item:7" in deleted
