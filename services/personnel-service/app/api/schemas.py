"""Pydantic schemas for the personnel-service.

Manages staff members and their roles within a restaurant.
Soft-delete (is_active flag) is used instead of hard deletes to preserve
historical records (e.g., for payroll auditing).
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmploymentType(str, Enum):
    """Employment contract type."""

    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACTOR = "CONTRACTOR"


# ---------------------------------------------------------------------------
# Role schemas
# ---------------------------------------------------------------------------


class RoleBase(BaseModel):
    """A named role that can be assigned to staff members (e.g. 'Head Chef', 'Waiter')."""

    name: str = Field(..., min_length=1, max_length=100, description="Role name")
    description: str | None = Field(None, max_length=512)


class RoleCreate(RoleBase):
    """Payload for creating a new role."""


class RoleRead(RoleBase):
    """Role response."""

    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Staff member schemas
# ---------------------------------------------------------------------------


class StaffMemberBase(BaseModel):
    """Core fields of a staff member."""

    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Work email — must be unique within the tenant")
    phone: str | None = Field(None, max_length=50)
    employment_type: EmploymentType = Field(EmploymentType.FULL_TIME)
    role_id: int | None = Field(None, description="Assigned role id")
    pin: str | None = Field(None, min_length=4, max_length=8, description="POS login PIN (stored hashed in production)")


class StaffMemberCreate(StaffMemberBase):
    """Payload for adding a new staff member."""


class StaffMemberUpdate(BaseModel):
    """Partial payload for updating a staff member."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = None
    employment_type: EmploymentType | None = None
    role_id: int | None = None
    pin: str | None = Field(None, min_length=4, max_length=8)


class StaffMemberRead(StaffMemberBase):
    """Staff member response."""

    id: int
    tenant_id: str
    is_active: bool
    role: RoleRead | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
