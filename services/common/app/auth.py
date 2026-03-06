from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode
import httpx

from common.app.config import Settings, get_settings


@dataclass(frozen=True)
class CurrentUser:
    """Authenticated caller context derived from the Keycloak access token."""

    subject: str
    username: str | None
    email: str | None
    tenant_id: str | None
    roles: tuple[str, ...]
    raw_claims: Mapping[str, Any]


@lru_cache(maxsize=8)
def _jwks(jwks_url: str) -> dict[str, Any]:
    """Fetch and cache JWKS from Keycloak.

    JWKS is cached per-process; rotate by restarting services when keys change.
    """
    with httpx.Client(timeout=5.0) as client:
        response = client.get(jwks_url)
        response.raise_for_status()
        data = response.json()
    keys = data.get("keys") or []
    # Normalise to a dict keyed by kid for quick lookup
    return {key["kid"]: key for key in keys if "kid" in key}


def _get_signing_key(token: str, settings: Settings) -> dict[str, Any]:
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    alg = headers.get("alg")

    if alg not in settings.keycloak_allowed_algs:
        msg = "Token signed with disallowed algorithm"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

    if not kid:
        msg = "Token header missing key id (kid)"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

    realm_url = f"{settings.keycloak_url}/realms/{settings.keycloak_realm}"
    jwks_url = f"{realm_url}/protocol/openid-connect/certs"
    keys = _jwks(jwks_url)
    key_data = keys.get(kid)
    if not key_data:
        msg = "Signing key not found for token"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

    return key_data


def _decode_token(token: str, settings: Settings) -> dict[str, Any]:
    key_data = _get_signing_key(token, settings)
    public_key = jwk.construct(key_data, settings.keycloak_allowed_algs[0])

    message, encoded_sig = token.rsplit(".", 1)
    decoded_sig = base64url_decode(encoded_sig.encode("utf-8"))

    if not public_key.verify(message.encode("utf-8"), decoded_sig):
        msg = "Token signature verification failed"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

    try:
        claims = jwt.decode(
            token,
            public_key.to_pem().decode("utf-8"),
            algorithms=list(settings.keycloak_allowed_algs),
            options={
                "verify_aud": False,
                "require_exp": True,
                "require_iat": True,
            },
        )
    except JWTError as exc:
        msg = "Invalid authentication token"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg) from exc

    # Keycloak access tokens commonly expose client identity in azp and may not
    # include the client_id inside aud unless an audience mapper is configured.
    aud_claim = claims.get("aud")
    aud_ok = False
    if isinstance(aud_claim, str):
        aud_ok = aud_claim == settings.keycloak_audience
    elif isinstance(aud_claim, list):
        aud_ok = settings.keycloak_audience in {str(v) for v in aud_claim}
    azp_ok = str(claims.get("azp", "")) == settings.keycloak_audience
    if not (aud_ok or azp_ok):
        msg = "Invalid authentication token audience"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

    # In local Docker setups, Keycloak may mint tokens with a browser-reachable
    # hostname (e.g. host.docker.internal) while services resolve it as "keycloak".
    # Validate realm/path strictly while allowing hostname differences.
    issuer = str(claims.get("iss", ""))
    parsed = urlparse(issuer)
    expected_realm_path = f"/realms/{settings.keycloak_realm}"
    if not parsed.path.endswith(expected_realm_path):
        msg = "Invalid authentication token issuer"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

    return claims


def _extract_roles(claims: Mapping[str, Any], *, client_id: str) -> tuple[str, ...]:
    roles: set[str] = set()

    realm_access = claims.get("realm_access") or {}
    realm_roles = realm_access.get("roles") or []
    roles.update(str(r) for r in realm_roles)

    resource_access = claims.get("resource_access") or {}
    client_access = resource_access.get(client_id) or {}
    client_roles = client_access.get("roles") or []
    roles.update(str(r) for r in client_roles)

    return tuple(sorted(roles))


def _build_current_user(claims: Mapping[str, Any], settings: Settings) -> CurrentUser:
    subject = str(claims.get("sub", ""))
    if not subject:
        msg = "Token missing subject"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

    username = claims.get("preferred_username") or claims.get("upn") or None
    email = claims.get("email") or None
    # Tenant can be modelled as a dedicated claim; fall back to custom claim name if provided
    tenant_id_claim = settings.keycloak_tenant_claim
    tenant_id = claims.get(tenant_id_claim) if tenant_id_claim else None

    roles = _extract_roles(claims, client_id=settings.keycloak_audience)

    return CurrentUser(
        subject=subject,
        username=str(username) if username is not None else None,
        email=str(email) if email is not None else None,
        tenant_id=str(tenant_id) if tenant_id is not None else None,
        roles=roles,
        raw_claims=dict(claims),
    )


def get_current_user(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> CurrentUser:
    """FastAPI dependency that authenticates the caller using a Bearer token.

    The Authorization header must contain a Keycloak access token:

        Authorization: Bearer <access-token>
    """
    auth_header = request.headers.get("authorization") or ""
    scheme, _, credentials = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not credentials:
        msg = "Missing or invalid Authorization header"
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

    claims = _decode_token(credentials, settings)
    return _build_current_user(claims, settings)


def require_roles(*required_roles: str):
    """Return a dependency that enforces presence of at least one required role."""

    def dependency(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        user_roles = set(current_user.roles)
        if required_roles and not user_roles.intersection(required_roles):
            msg = "Insufficient permissions"
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=msg)
        return current_user

    return dependency
