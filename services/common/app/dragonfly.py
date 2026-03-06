"""Dragonfly (Redis protocol) helpers for caching and coordination."""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from redis import Redis
from redis.exceptions import RedisError

from common.app.config import get_settings

logger = logging.getLogger(__name__)

_CLIENT: Redis | None = None
T = TypeVar("T")


def _client() -> Redis:
    global _CLIENT
    if _CLIENT is None:
        settings = get_settings()
        _CLIENT = Redis.from_url(settings.redis_url, decode_responses=True)
    return _CLIENT


def _safe(callable_name: str, fn: Callable[[], T]) -> T | None:
    try:
        return fn()
    except RedisError as exc:
        logger.warning("Dragonfly %s failed: %s", callable_name, exc)
        return None


def cache_get_json(key: str) -> Any | None:
    raw = _safe("get", lambda: _client().get(key))
    if not raw:
        return None
    try:
        return json.loads(str(raw))
    except json.JSONDecodeError:
        return None


def cache_set_json(key: str, value: Any, ttl_seconds: int) -> None:
    payload = json.dumps(value, separators=(",", ":"), default=str)
    _safe("set", lambda: _client().set(key, payload, ex=ttl_seconds))


def cache_delete(*keys: str) -> None:
    if not keys:
        return
    _safe("delete", lambda: _client().delete(*keys))


def cache_delete_prefix(prefix: str) -> None:
    def _delete() -> int:
        deleted = 0
        for key in _client().scan_iter(match=f"{prefix}*"):
            deleted += int(_client().delete(str(key)))
        return deleted

    _safe("scan/delete", _delete)


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after_seconds: int


def check_rate_limit(
    *,
    scope: str,
    identity: str,
    max_requests: int,
    window_seconds: int,
) -> RateLimitResult:
    key = f"ratelimit:{scope}:{identity}"

    def _increment() -> tuple[int, int]:
        client = _client()
        current = int(client.incr(key))
        if current == 1:
            client.expire(key, window_seconds)
        ttl = int(client.ttl(key))
        return current, max(ttl, 0)

    result = _safe("incr", _increment)
    if result is None:
        # Fail open if Dragonfly is unavailable.
        return RateLimitResult(allowed=True, remaining=max_requests, retry_after_seconds=0)

    current, ttl = result
    allowed = current <= max_requests
    remaining = max(max_requests - current, 0)
    return RateLimitResult(allowed=allowed, remaining=remaining, retry_after_seconds=ttl)


@dataclass(frozen=True)
class LockHandle:
    key: str
    token: str


def acquire_lock(*, key: str, ttl_seconds: int) -> LockHandle | None:
    token = str(uuid.uuid4())
    acquired = _safe("set-nx", lambda: _client().set(key, token, nx=True, ex=ttl_seconds))
    if acquired:
        return LockHandle(key=key, token=token)
    return None


def release_lock(lock: LockHandle) -> None:
    # Delete only if token matches, so we never release someone else's lock.
    script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
      return redis.call("del", KEYS[1])
    else
      return 0
    end
    """
    _safe("lua-release", lambda: _client().eval(script, 1, lock.key, lock.token))
