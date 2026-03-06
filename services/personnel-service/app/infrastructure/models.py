"""ORM models for the personnel-service."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.app.database import Base, TimestampMixin


class Role(Base):
    """A staff role (e.g. Head Chef, Waiter, Manager).

    Roles are scoped to the tenant; one tenant may have different role names
    from another.
    """

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)

    staff: Mapped[list["StaffMember"]] = relationship("StaffMember", back_populates="role")


class StaffMember(TimestampMixin, Base):
    """A staff member working at a restaurant.

    ``is_active`` drives soft-delete behaviour: deactivated staff are excluded
    from operational queries but retained for historical/payroll reporting.
    """

    __tablename__ = "staff_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    employment_type: Mapped[str] = mapped_column(String(32), nullable=False, default="FULL_TIME")
    role_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)
    # MVP: store PIN in plaintext; replace with bcrypt hash in production
    pin: Mapped[str | None] = mapped_column(String(8), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    role: Mapped["Role | None"] = relationship("Role", back_populates="staff")
