"""HTTP controller for the personnel-service."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from common.app.database import get_db_session
from common.app.dependencies import PaginationDep, TenantIdDep

from app.api.schemas import (
    RoleCreate,
    RoleRead,
    StaffMemberCreate,
    StaffMemberRead,
    StaffMemberUpdate,
)
from app.domain.services import PersonnelService
from app.infrastructure.repositories import PersonnelRepository, RoleRepository

router = APIRouter()


def _get_service(
    db: Session = Depends(get_db_session),
    tenant_id: TenantIdDep = Depends(),
) -> PersonnelService:
    return PersonnelService(
        personnel_repo=PersonnelRepository(db=db, tenant_id=tenant_id),
        role_repo=RoleRepository(db=db, tenant_id=tenant_id),
    )


# ---------------------------------------------------------------------------
# Role endpoints
# ---------------------------------------------------------------------------


@router.get("/roles/", response_model=list[RoleRead], summary="List staff roles")
def list_roles(service: PersonnelService = Depends(_get_service)) -> list[RoleRead]:
    """List all available staff roles for this tenant."""
    return service.list_roles()


@router.post("/roles/", response_model=RoleRead, status_code=status.HTTP_201_CREATED, summary="Create a role")
def create_role(payload: RoleCreate, service: PersonnelService = Depends(_get_service)) -> RoleRead:
    """Create a new staff role (e.g. Head Chef, Waiter)."""
    return service.create_role(payload)


# ---------------------------------------------------------------------------
# Staff endpoints
# ---------------------------------------------------------------------------


@router.get("/staff/", response_model=list[StaffMemberRead], summary="List staff members")
def list_staff(
    include_inactive: bool = Query(default=False, description="Include deactivated staff"),
    pagination: PaginationDep = Depends(),
    service: PersonnelService = Depends(_get_service),
) -> list[StaffMemberRead]:
    """List staff members; by default only active staff are returned."""
    return service.list_staff(include_inactive=include_inactive, skip=pagination.skip, limit=pagination.limit)


@router.post(
    "/staff/", response_model=StaffMemberRead, status_code=status.HTTP_201_CREATED, summary="Add a staff member"
)
def create_staff_member(
    payload: StaffMemberCreate, service: PersonnelService = Depends(_get_service)
) -> StaffMemberRead:
    """Add a new staff member."""
    try:
        return service.create_staff_member(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.get("/staff/{staff_id}", response_model=StaffMemberRead, summary="Get a staff member")
def get_staff_member(staff_id: int, service: PersonnelService = Depends(_get_service)) -> StaffMemberRead:
    """Return a single staff member."""
    member = service.get_staff_member(staff_id)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found")
    return member


@router.patch("/staff/{staff_id}", response_model=StaffMemberRead, summary="Update a staff member")
def update_staff_member(
    staff_id: int,
    payload: StaffMemberUpdate,
    service: PersonnelService = Depends(_get_service),
) -> StaffMemberRead:
    """Partially update a staff member."""
    try:
        member = service.update_staff_member(staff_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found")
    return member


@router.delete("/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deactivate a staff member")
def deactivate_staff_member(staff_id: int, service: PersonnelService = Depends(_get_service)) -> None:
    """Soft-delete a staff member (marks as inactive, data is retained)."""
    if not service.deactivate_staff_member(staff_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff member not found")
