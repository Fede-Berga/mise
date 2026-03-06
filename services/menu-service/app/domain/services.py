from typing import Sequence

from common.app.config import get_settings
from common.app.dragonfly import cache_delete, cache_get_json, cache_set_json

from ..api.schemas import MenuItemCreate, MenuItemRead, MenuItemUpdate
from ..infrastructure.repositories import MenuRepository


class MenuService:
    def __init__(self, repo: MenuRepository):
        self._repo = repo

    @property
    def _tenant_id(self) -> str:
        return self._repo.tenant_id

    def _list_key(self) -> str:
        return f"cache:menu:{self._tenant_id}:items"

    def _item_key(self, item_id: int) -> str:
        return f"cache:menu:{self._tenant_id}:item:{item_id}"

    def _invalidate_menu_cache(self, item_id: int | None = None) -> None:
        cache_delete(self._list_key())
        if item_id is not None:
            cache_delete(self._item_key(item_id))

    def list_items(self) -> Sequence[MenuItemRead]:
        settings = get_settings()
        cache_key = self._list_key()
        cached = cache_get_json(cache_key)
        if isinstance(cached, list):
            return [MenuItemRead.model_validate(item) for item in cached]

        items = [MenuItemRead.model_validate(item) for item in self._repo.list_items()]
        cache_set_json(cache_key, [item.model_dump(mode="json") for item in items], settings.menu_cache_ttl_seconds)
        return items

    def get_item(self, item_id: int) -> MenuItemRead | None:
        settings = get_settings()
        cache_key = self._item_key(item_id)
        cached = cache_get_json(cache_key)
        if isinstance(cached, dict):
            return MenuItemRead.model_validate(cached)

        item = self._repo.get_item(item_id)
        if not item:
            return None
        parsed = MenuItemRead.model_validate(item)
        cache_set_json(cache_key, parsed.model_dump(mode="json"), settings.menu_cache_ttl_seconds)
        return parsed

    def create_item(self, data: MenuItemCreate) -> MenuItemRead:
        item = self._repo.create_item(data)
        parsed = MenuItemRead.model_validate(item)
        self._invalidate_menu_cache(item_id=parsed.id)
        return parsed

    def update_item(self, item_id: int, data: MenuItemUpdate) -> MenuItemRead | None:
        item = self._repo.update_item(item_id, data)
        if not item:
            return None
        parsed = MenuItemRead.model_validate(item)
        self._invalidate_menu_cache(item_id=item_id)
        return parsed

    def delete_item(self, item_id: int) -> bool:
        deleted = self._repo.delete_item(item_id)
        if deleted:
            self._invalidate_menu_cache(item_id=item_id)
        return deleted


def get_menu_service(repo: MenuRepository) -> MenuService:
    return MenuService(repo=repo)
