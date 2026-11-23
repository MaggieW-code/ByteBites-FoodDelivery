"""Auth-only fixtures. The write_json fixture comes from backend/tests/conftest.py."""

from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from backend.app.repositories.account_repository import AccountRepository
from backend.app.repositories.session_repository import SessionRepository
from backend.app.services.auth_service import AuthService
from backend.app.services.password_hashing import hash_password
from backend.tests.auth.auth_helpers import TEST_PASSWORD, TOKEN_LIFETIME, FakeClock


# scrypt is slow on purpose; hash once per session. A str is immutable, so sharing is safe.
@pytest.fixture(scope="session")
def test_password_hash() -> str:
    return hash_password(TEST_PASSWORD)


@pytest.fixture
def account_records(test_password_hash: str) -> list[dict[str, Any]]:
    shared = dict(phone="250-555-0100", password_hash=test_password_hash)
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
