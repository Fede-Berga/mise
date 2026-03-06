"""Database engine, session factory, and shared declarative base for all Mise services.

Design decisions:
- A single ``Base`` is shared across services so that Alembic migrations can
  introspect the full model graph from one entry-point.
- ``TimestampMixin`` adds ``created_at`` / ``updated_at`` to every table that
  inherits from it — using server-side ``func.now()`` so the database clock is
  authoritative.
- The session is yielded (not returned) so FastAPI/pytest can clean up reliably
  inside a ``try/finally`` block.
"""

from __future__ import annotations

from datetime import datetime
from typing import Generator

from sqlalchemy import DateTime, create_engine, func, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from common.app.config import get_settings

# ---------------------------------------------------------------------------
# Declarative base — all ORM models inherit from this
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    """Root declarative base shared by all Mise services."""


class TimestampMixin:
    """Mixin that adds ``created_at`` and ``updated_at`` audit columns.

    Include this mixin in any model that should track row-level timestamps::

        class MyModel(TimestampMixin, Base):
            __tablename__ = "my_table"
            ...
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# ---------------------------------------------------------------------------
# Engine & session factory
# ---------------------------------------------------------------------------

_settings = get_settings()

engine = create_engine(
    str(_settings.database_url),
    pool_size=_settings.db_pool_size,
    max_overflow=_settings.db_max_overflow,
    pool_timeout=_settings.db_pool_timeout,
    # Echo SQL only in non-JSON (dev) mode to avoid log noise in production
    echo=not _settings.log_json,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # safer for async / background tasks
)


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------


def get_db_session() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session and guarantee cleanup.

    Usage in a FastAPI route::

        @router.get("/")
        def my_route(db: Session = Depends(get_db_session)):
            ...

    Prefer the typed alias ``DbSessionDep`` from ``common.app.dependencies``.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
