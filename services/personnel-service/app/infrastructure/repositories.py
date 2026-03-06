"""Repository layer for the personnel-service."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import RoleCreate, StaffMemberCreate, StaffMemberUpdate
from app.infrastructure.models import Role, StaffMember


class RoleRepository:
    """Data access for staff roles, tenant-scoped."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self._db = db
        self._tenant_id = tenant_id

    def list(self) -> list[Role]:
        stmt = select(Role).where(Role.tenant_id == self._tenant_id).order_by(Role.name)
        return list(self._db.execute(stmt).scalars().all())

    def get(self, role_id: int) -> Role | None:
        stmt = select(Role).where(Role.id == role_id, Role.tenant_id == self._tenant_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def create(self, data: RoleCreate) -> Role:
        role = Role(tenant_id=self._tenant_id, name=data.name, description=data.description)
        self._db.add(role)
        self._db.commit()
        self._db.refresh(role)
        return role


class PersonnelRepository:
    """Data access for staff members, tenant-scoped.

    Active-only queries exclude deactivated staff; include_inactive=True
    is provided for administrative views.
    """

    def __init__(self, db: Session, tenant_id: str) -> None:
        self._db = db
        self._tenant_id = tenant_id

    def _base_query(self, include_inactive: bool = False):
        stmt = select(StaffMember).where(StaffMember.tenant_id == self._tenant_id)
        if not include_inactive:
            stmt = stmt.where(StaffMember.is_active == True)  # noqa: E712
        return stmt

    def list(self, *, include_inactive: bool = False, skip: int = 0, limit: int = 50) -> list[StaffMember]:
        stmt = self._base_query(include_inactive).order_by(StaffMember.last_name).offset(skip).limit(limit)
        return list(self._db.execute(stmt).scalars().all())

    def get(self, staff_id: int, *, include_inactive: bool = False) -> StaffMember | None:
        stmt = self._base_query(include_inactive).where(StaffMember.id == staff_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def create(self, data: StaffMemberCreate) -> StaffMember:
        member = StaffMember(
            tenant_id=self._tenant_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            employment_type=data.employment_type.value,
            role_id=data.role_id,
            pin=data.pin,
            is_active=True,
        )
        self._db.add(member)
        self._db.commit()
        self._db.refresh(member)
        return member

    def update(self, staff_id: int, data: StaffMemberUpdate) -> StaffMember | None:
        member = self.get(staff_id)
        if not member:
            return None
        patch = data.model_dump(exclude_unset=True)
        if "employment_type" in patch and patch["employment_type"]:
            patch["employment_type"] = patch["employment_type"].value
        for field, value in patch.items():
            setattr(member, field, value)
        self._db.commit()
        self._db.refresh(member)
        return member

    def deactivate(self, staff_id: int) -> bool:
        """Soft-delete: mark staff member as inactive rather than deleting."""
        member = self.get(staff_id)
        if not member:
            return False
        member.is_active = False
        self._db.commit()
        return True
