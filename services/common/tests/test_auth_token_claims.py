"""Tests for Keycloak token audience validation behavior."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from common.app import auth
from common.app.config import Settings

FAKE_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6InRlc3QifQ.eyJzdWIiOiJ1c2VyLTEifQ.c2ln"  # noqa: S105


@pytest.fixture
def settings() -> Settings:
    return Settings(keycloak_audience="mise-web")


@pytest.fixture
def patched_crypto(monkeypatch):
    monkeypatch.setattr(auth, "_get_signing_key", lambda _token, _settings: {"kty": "RSA"})

    class _PublicKey:
        def verify(self, _message: bytes, _sig: bytes) -> bool:
            return True

        def to_pem(self) -> bytes:
            return b"fake-pem"

    monkeypatch.setattr(auth.jwk, "construct", lambda *_args, **_kwargs: _PublicKey())


def test_decode_token_accepts_azp_when_aud_not_matching(monkeypatch, settings, patched_crypto):
    claims = {
        "sub": "user-1",
        "iss": "http://localhost:8080/auth/realms/mise",
        "aud": "account",
        "azp": "mise-web",
        "exp": 9999999999,
        "iat": 1111111111,
    }
    monkeypatch.setattr(auth.jwt, "decode", lambda *args, **kwargs: claims)

    decoded = auth._decode_token(FAKE_TOKEN, settings)

    assert decoded["azp"] == "mise-web"


def test_decode_token_rejects_when_neither_aud_nor_azp_match(monkeypatch, settings, patched_crypto):
    claims = {
        "sub": "user-1",
        "iss": "http://localhost:8080/auth/realms/mise",
        "aud": "account",
        "azp": "different-client",
        "exp": 9999999999,
        "iat": 1111111111,
    }
    monkeypatch.setattr(auth.jwt, "decode", lambda *args, **kwargs: claims)

    with pytest.raises(HTTPException) as exc:
        auth._decode_token(FAKE_TOKEN, settings)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid authentication token audience"
