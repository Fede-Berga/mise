"""HTTP controller for the order-service.

CRUD operations for orders and order status transitions.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status

from common.app.config import get_settings
from common.app.dependencies import CurrentUserDep, DbSessionDep, TenantIdDep
from common.app.dragonfly import RateLimitResult, check_rate_limit

from app.api.schemas import OrderCreate, OrderRead, OrderStatus, OrderStatusUpdate
from app.domain.services import OrderService
from app.infrastructure.repositories import OrderRepository

router = APIRouter()


# ---------------------------------------------------------------------------
# Dependency factories
# ---------------------------------------------------------------------------


def _get_order_repo(db: DbSessionDep, tenant_id: TenantIdDep) -> OrderRepository:
    """Construct a tenant-scoped order repository."""
    return OrderRepository(db=db, tenant_id=tenant_id)


def _get_service(repo: OrderRepository = Depends(_get_order_repo)) -> OrderService:
    """Construct the order domain service."""
    return OrderService(repo=repo)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/", response_model=list[OrderRead], summary="List orders")
def list_orders(
    status: Optional[OrderStatus] = Query(default=None),
    service: OrderService = Depends(_get_service),
) -> list[OrderRead]:
    """Return all orders, optionally filtered by status."""
    return list(service.list_orders(status=status))


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED, summary="Place an order")
def create_order(
    request: Request,
    payload: OrderCreate,
    tenant_id: TenantIdDep,
    current_user: CurrentUserDep,
    service: OrderService = Depends(_get_service),
    authorization: str | None = Header(default=None, alias="Authorization"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> OrderRead:
    """Place a new order with rate limiting and idempotency support."""
    settings = get_settings()
    client_host = request.client.host if request.client else "anonymous"
    identity = current_user.subject or client_host
    limiter: RateLimitResult = check_rate_limit(
        scope="orders:create",
        identity=f"{tenant_id}:{identity}",
        max_requests=settings.rate_limit_max_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )
    if not limiter.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded for order creation",
            headers={"Retry-After": str(limiter.retry_after_seconds)},
        )
    try:
        return service.create_order(
            payload,
            tenant_id=tenant_id,
            auth_header=authorization,
            idempotency_key=idempotency_key,
            actor_id=current_user.subject,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/{order_id}", response_model=OrderRead, summary="Get an order")
def get_order(
    order_id: int,
    service: OrderService = Depends(_get_service),
) -> OrderRead:
    order = service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.patch("/{order_id}/status", response_model=OrderRead, summary="Update order status")
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    tenant_id: TenantIdDep,
    service: OrderService = Depends(_get_service),
) -> OrderRead:
    try:
        order = service.update_status(order_id, payload, tenant_id=tenant_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
