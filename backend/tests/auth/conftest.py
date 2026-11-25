"""Auth-only fixtures. The write_json and client fixtures come from backend/tests/conftest.py."""

from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.app.dependencies.auth import get_account_service, get_auth_service
from backend.app.models.accounts.auth_model import SignInRequest
from backend.app.repositories.accounts.account_repository import AccountRepository
from backend.app.repositories.accounts.session_repository import SessionRepository
from backend.app.services.accounts.account_service import AccountService
from backend.app.services.accounts.auth_service import AuthService
from backend.app.services.accounts.password_hashing import hash_password
from backend.tests.auth.auth_helpers import TEST_PASSWORD, TOKEN_LIFETIME, FakeClock
from main import app


# scrypt is slow on purpose; hash once per session. A str is immutable, so sharing is safe.
@pytest.fixture(scope="session")
def test_password_hash() -> str:
    return hash_password(TEST_PASSWORD)


@pytest.fixture
def account_records(test_password_hash: str) -> list[dict[str, Any]]:
    shared = dict(phone="+12505550100", password_hash=test_password_hash)
    return [
        dict(id="cust_001", full_name="Cara Customer", email="cara@example.com", role="customer", is_active=True) | shared,
        dict(id="cust_002", full_name="Dana Inactive", email="dana@example.com", role="customer", is_active=False) | shared,
        dict(id="ownr_001", full_name="Omar Owner", email="omar@example.com", role="restaurant_owner", is_active=True)
        | shared,
    ]


@pytest.fixture
def session_records() -> list[dict[str, Any]]:
    return [
        dict(
            token_hash="hash_of_cara_token",
            account_id="cust_001",
            created_at="2026-11-22T12:00:00Z",
            expires_at="2026-11-22T13:00:00Z",
        ),
    ]


@pytest.fixture
def accounts_file(write_json: Callable[[str, Any], Path], account_records: list[dict[str, Any]]) -> Path:
    return write_json("accounts.json", account_records)


@pytest.fixture
def sessions_file(write_json: Callable[[str, Any], Path], session_records: list[dict[str, Any]]) -> Path:
    return write_json("sessions.json", session_records)


@pytest.fixture
def account_repository(accounts_file: Path) -> AccountRepository:
    return AccountRepository(accounts_file)


@pytest.fixture
def session_repository(sessions_file: Path) -> SessionRepository:
    return SessionRepository(sessions_file)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(datetime(2026, 11, 22, 12, 30, tzinfo=timezone.utc))


@pytest.fixture
def auth_service(
    account_repository: AccountRepository, session_repository: SessionRepository, clock: FakeClock
) -> AuthService:
    return AuthService(account_repository, session_repository, token_lifetime=TOKEN_LIFETIME, clock=clock)


@pytest.fixture
def account_service(account_repository: AccountRepository) -> AccountService:
    return AccountService(account_repository)


@pytest.fixture
def client(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, auth_service: AuthService, account_service: AccountService
) -> TestClient:
    monkeypatch.setitem(app.dependency_overrides, get_auth_service, lambda: auth_service)
    monkeypatch.setitem(app.dependency_overrides, get_account_service, lambda: account_service)
    return client


@pytest.fixture
def auth_headers(auth_service: AuthService) -> Callable[[str], dict[str, str]]:
    """Factory fixture that returns _headers(email)"""

    def _headers(email: str) -> dict[str, str]:
        sign_in_request = SignInRequest(email=email, password=TEST_PASSWORD)
        token = auth_service.sign_in(sign_in_request).access_token
        return {"Authorization": f"Bearer {token}"}

    return _headers
