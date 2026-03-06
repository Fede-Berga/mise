"""Domain service for the personnel-service."""

from __future__ import annotations

import logging

from app.api.schemas import (
    EmploymentType,
    RoleCreate,
    RoleRead,
    StaffMemberCreate,
    StaffMemberRead,
    StaffMemberUpdate,
)
from app.infrastructure.models import Role, StaffMember
from app.infrastructure.repositories import PersonnelRepository, RoleRepository

logger = logging.getLogger(__name__)


class PersonnelService:
    """Orchestrates personnel management operations."""

    def __init__(self, personnel_repo: PersonnelRepository, role_repo: RoleRepository) -> None:
        self._personnel = personnel_repo
        self._roles = role_repo

    @staticmethod
    def _role_to_read(role: Role) -> RoleRead:
        return RoleRead.model_validate(role)

    @staticmethod
    def _staff_to_read(member: StaffMember) -> StaffMemberRead:
        """Convert ORM staff member to Pydantic read schema including the associated role."""
        role_read = RoleRead.model_validate(member.role) if member.role else None
        return StaffMemberRead(
            id=member.id,
            tenant_id=member.tenant_id,
            first_name=member.first_name,
            last_name=member.last_name,
            email=member.email,
            phone=member.phone,
            employment_type=EmploymentType(member.employment_type),
            role_id=member.role_id,
            pin=member.pin,
            is_active=member.is_active,
            role=role_read,
            created_at=member.created_at,
            updated_at=member.updated_at,
        )

    # ------------------------------------------------------------------
    # Role operations
    # ------------------------------------------------------------------

    def list_roles(self) -> list[RoleRead]:
        return [self._role_to_read(r) for r in self._roles.list()]

    def create_role(self, data: RoleCreate) -> RoleRead:
        role = self._roles.create(data)
        logger.info("Role created", extra={"role_id": role.id, "name": role.name})
        return self._role_to_read(role)

    # ------------------------------------------------------------------
    # Staff operations
    # ------------------------------------------------------------------

    def list_staff(self, *, include_inactive: bool = False, skip: int = 0, limit: int = 50) -> list[StaffMemberRead]:
        return [self._staff_to_read(m) for m in self._personnel.list(include_inactive=include_inactive, skip=skip, limit=limit)]

    def get_staff_member(self, staff_id: int) -> StaffMemberRead | None:
        member = self._personnel.get(staff_id)
        return self._staff_to_read(member) if member else None

    def create_staff_member(self, data: StaffMemberCreate) -> StaffMemberRead:
        """Create a staff member, validating that the assigned role exists if provided."""
        if data.role_id and not self._roles.get(data.role_id):
            raise ValueError(f"Role {data.role_id} not found")
        member = self._personnel.create(data)
        logger.info("Staff member created", extra={"staff_id": member.id, "email": member.email})
        return self._staff_to_read(member)

    def update_staff_member(self, staff_id: int, data: StaffMemberUpdate) -> StaffMemberRead | None:
        if data.role_id and not self._roles.get(data.role_id):
            raise ValueError(f"Role {data.role_id} not found")
        member = self._personnel.update(staff_id, data)
        return self._staff_to_read(member) if member else None

    def deactivate_staff_member(self, staff_id: int) -> bool:
        """Soft-delete a staff member (marks is_active=False)."""
        deactivated = self._personnel.deactivate(staff_id)
        if deactivated:
            logger.info("Staff member deactivated", extra={"staff_id": staff_id})
        return deactivated
