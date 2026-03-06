from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from common.app.dependencies import TenantIdDep

from ..api.schemas import MenuItemCreate, MenuItemUpdate
from .models import MenuItem


class MenuRepository:
    def __init__(self, db: Session, tenant_id: str):
        self._db = db
        self._tenant_id = tenant_id

    @property
    def tenant_id(self) -> str:
        return self._tenant_id

    def list_items(self) -> Sequence[MenuItem]:
        stmt = select(MenuItem).where(MenuItem.tenant_id == self._tenant_id)
        return self._db.execute(stmt).scalars().all()

    def get_item(self, item_id: int) -> MenuItem | None:
        stmt = select(MenuItem).where(MenuItem.id == item_id, MenuItem.tenant_id == self._tenant_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def create_item(self, data: MenuItemCreate) -> MenuItem:
        item = MenuItem(
            tenant_id=self._tenant_id,
            name=data.name,
            description=data.description,
            price=data.price,
            is_available=data.is_available,
        )
        self._db.add(item)
        self._db.commit()
        self._db.refresh(item)
        return item

    def update_item(self, item_id: int, data: MenuItemUpdate) -> MenuItem | None:
        item = self.get_item(item_id)
        if not item:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        self._db.commit()
        self._db.refresh(item)
        return item

    def delete_item(self, item_id: int) -> bool:
        item = self.get_item(item_id)
        if not item:
            return False
        self._db.delete(item)
        self._db.commit()
        return True


def get_menu_repository(db: Session, tenant_id: str) -> MenuRepository:
    return MenuRepository(db=db, tenant_id=tenant_id)
