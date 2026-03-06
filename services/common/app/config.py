from __future__ import annotations

from pydantic import AnyUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralised configuration for all Mise services.

    Values are loaded from environment variables (no prefix).
    A ``.env`` file is also read when present.
    """

    # --- Service identity ---
    service_name: str = "mise-service"
    log_level: str = "INFO"
    log_json: bool = True

    # --- Database ---
    database_url: AnyUrl = "postgresql+psycopg://mise:mise@postgres:5432/mise"  # type: ignore[assignment]
    database_schema: str = "public"
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30

    # --- Multi-tenancy ---
    tenant_id_header: str = "X-Tenant-Id"
    default_tenant_id: str = "restaurant-0001"

    # --- NATS ---
    nats_url: str = "nats://nats:4222"

    # --- Service URLs (for HTTP calls between services) ---
    menu_svc_url: str = "http://menu-svc:8000"
    order_svc_url: str = "http://order-svc:8000"

    # --- Redis / Dragonfly ---
    redis_url: str = "redis://dragonfly:6379/0"
    menu_cache_ttl_seconds: int = 30
    idempotency_ttl_seconds: int = 300
    rate_limit_window_seconds: int = 60
    rate_limit_max_requests: int = 120
    order_status_lock_ttl_seconds: int = 10

    # --- Keycloak IAM ---
    keycloak_url: str = "http://keycloak:8080/auth"
    keycloak_realm: str = "mise"
    keycloak_audience: str = "mise-web"
    keycloak_allowed_algs: tuple[str, ...] = ("RS256",)
    # Optional claim in the access token that carries tenant identifier, e.g. "tenant_id"
    keycloak_tenant_claim: str | None = None

    # --- OpenTelemetry ---
    otel_exporter_endpoint: str = ""
    otel_enabled: bool = False

    model_config = {
        "env_prefix": "",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


def get_settings() -> Settings:
    return Settings()
