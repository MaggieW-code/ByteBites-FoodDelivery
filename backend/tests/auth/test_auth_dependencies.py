"""The auth dependencies on a small app of their own; the real routes come in the routes branch."""

from collections.abc import Iterator
from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.app.dependencies.auth import get_auth_service, get_current_account, require_role
from backend.app.models.auth_model import AuthenticatedAccount, SignInRequest
from backend.app.services.auth_service import AuthService
from backend.tests.auth.auth_helpers import TEST_PASSWORD, TOKEN_LIFETIME, FakeClock

probe_app = FastAPI()


@probe_app.get("/whoami")
def whoami(account: Annotated[AuthenticatedAccount, Depends(get_current_account)]) -> AuthenticatedAccount:
    return account


@probe_app.get("/owners-only", dependencies=[Depends(require_role("restaurant_owner"))])
def owners_only() -> dict[str, bool]:
    return {"ok": True}


@pytest.fixture
def probe_client(auth_service: AuthService) -> Iterator[TestClient]:
    probe_app.dependency_overrides[get_auth_service] = lambda: auth_service
    with TestClient(probe_app) as client:
        yield client
    probe_app.dependency_overrides.clear()


def bearer(auth_service: AuthService, email: str) -> dict[str, str]:
    token = auth_service.sign_in(SignInRequest(email=email, password=TEST_PASSWORD)).access_token
    return {"Authorization": f"Bearer {token}"}


def test_valid_token_identifies_the_account(probe_client: TestClient, auth_service: AuthService) -> None:
    response = probe_client.get("/whoami", headers=bearer(auth_service, "cara@example.com"))

    assert response.status_code == 200
    assert response.json() == {"id": "cust_001", "role": "customer", "is_active": True}


@pytest.mark.parametrize(
    "headers",
    [{}, {"Authorization": "Bearer not-a-real-token"}, {"Authorization": "Basic abc"}, {"Authorization": "Bearer"}],
    ids=["no-header", "unknown-token", "wrong-scheme", "empty-token"],
)
def test_missing_or_bad_token_is_401_with_challenge(probe_client: TestClient, headers: dict[str, str]) -> None:
    response = probe_client.get("/whoami", headers=headers)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_expired_token_is_401(probe_client: TestClient, auth_service: AuthService, clock: FakeClock) -> None:
    headers = bearer(auth_service, "cara@example.com")
    clock.advance(TOKEN_LIFETIME)

    response = probe_client.get("/whoami", headers=headers)

    assert response.status_code == 401
    assert "expired" in response.json()["detail"]


def test_deactivated_account_is_403(probe_client: TestClient, auth_service: AuthService) -> None:
    headers = bearer(auth_service, "cara@example.com")
    auth_service.deactivate_account("cust_001")

    assert probe_client.get("/whoami", headers=headers).status_code == 403


@pytest.mark.parametrize(
    "email, expected_status",
    [("omar@example.com", 200), ("cara@example.com", 403), (None, 401)],
    ids=["owner", "customer", "anonymous"],
)
def test_require_role_gates_by_role(
    probe_client: TestClient, auth_service: AuthService, email: str | None, expected_status: int
) -> None:
    headers = bearer(auth_service, email) if email else {}

    assert probe_client.get("/owners-only", headers=headers).status_code == expected_status


def test_bearer_scheme_is_documented_in_openapi(probe_client: TestClient) -> None:
    schemes = probe_client.get("/openapi.json").json()["components"]["securitySchemes"]

    assert any(scheme["type"] == "http" and scheme["scheme"] == "bearer" for scheme in schemes.values())
