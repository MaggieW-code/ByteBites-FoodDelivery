import hashlib
from datetime import timedelta
from pathlib import Path

import pytest

from backend.app.models.account_model import AccountCreationRequest, CustomerAccount, RestaurantAccount
from backend.app.models.auth_model import AuthenticatedAccount, SignInRequest
from backend.app.repositories.account_repository import AccountRepository
from backend.app.repositories.session_repository import SessionRepository
from backend.app.services.auth_service import (
    AccountDeactivatedError,
    AccountNotFoundError,
    AuthService,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidTokenError,
    SessionExpiredError,
)
from backend.app.services.password_hashing import verify_password
from backend.tests.auth.auth_helpers import TEST_PASSWORD, TOKEN_LIFETIME, FakeClock


def sign_in(auth_service: AuthService, email: str = "cara@example.com", password: str = TEST_PASSWORD) -> str:
    return auth_service.sign_in(SignInRequest(email=email, password=password)).access_token


# --- sign in ---


def test_sign_in_returns_bearer_token_that_expires(auth_service: AuthService, clock: FakeClock) -> None:
    response = auth_service.sign_in(SignInRequest(email="  CARA@example.com", password=TEST_PASSWORD))

    assert response.token_type == "bearer"
    assert len(response.access_token) >= 32
    assert response.expires_at == clock() + TOKEN_LIFETIME


def test_sign_in_stores_only_a_hash_of_the_token(auth_service: AuthService, sessions_file: Path) -> None:
    token = sign_in(auth_service)

    stored = sessions_file.read_text(encoding="utf-8")
    assert token not in stored
    assert hashlib.sha256(token.encode()).hexdigest() in stored


@pytest.mark.parametrize(
    "email, password",
    [("cara@example.com", "wrong-password"), ("ghost@example.com", TEST_PASSWORD)],
    ids=["wrong-password", "unknown-email"],
)
def test_bad_credentials_raise_the_same_error(auth_service: AuthService, email: str, password: str) -> None:
    with pytest.raises(InvalidCredentialsError, match="^Invalid email or password$"):
        sign_in(auth_service, email, password)


def test_deactivated_account_cannot_sign_in(auth_service: AuthService) -> None:
    with pytest.raises(AccountDeactivatedError):
        sign_in(auth_service, "dana@example.com")


# --- resolve token ---


def test_resolve_token_returns_the_signed_in_account(auth_service: AuthService) -> None:
    token = sign_in(auth_service, "omar@example.com")

    assert auth_service.resolve_token(token) == AuthenticatedAccount(id="ownr_001", role="restaurant_owner", is_active=True)


def test_unknown_token_is_invalid(auth_service: AuthService) -> None:
    with pytest.raises(InvalidTokenError):
        auth_service.resolve_token("not-a-real-token")


def test_token_expires_and_its_session_is_removed(
    auth_service: AuthService, clock: FakeClock, session_repository: SessionRepository
) -> None:
    token = sign_in(auth_service)
    clock.advance(TOKEN_LIFETIME)

    with pytest.raises(SessionExpiredError):
        auth_service.resolve_token(token)
    assert session_repository.get_by_token_hash(hashlib.sha256(token.encode()).hexdigest()) is None


def test_token_still_works_just_before_expiry(auth_service: AuthService, clock: FakeClock) -> None:
    token = sign_in(auth_service)
    clock.advance(TOKEN_LIFETIME - timedelta(seconds=1))

    assert auth_service.resolve_token(token).id == "cust_001"


def test_deactivating_an_account_blocks_its_existing_token(auth_service: AuthService) -> None:
    token = sign_in(auth_service)

    auth_service.deactivate_account("cust_001")

    with pytest.raises(AccountDeactivatedError):
        auth_service.resolve_token(token)


# --- sign out ---


def test_sign_out_invalidates_the_token(auth_service: AuthService) -> None:
    token = sign_in(auth_service)

    auth_service.sign_out(token)

    with pytest.raises(InvalidTokenError):
        auth_service.resolve_token(token)


def test_sign_out_leaves_other_sessions_alone(auth_service: AuthService) -> None:
    cara_token = sign_in(auth_service)
    omar_token = sign_in(auth_service, "omar@example.com")

    auth_service.sign_out(cara_token)

    assert auth_service.resolve_token(omar_token).id == "ownr_001"


# --- accounts ---


def make_registration(email: str = "nina@example.com") -> AccountCreationRequest:
    return AccountCreationRequest(full_name="Nina New", email=email, phone="250-555-0123", password="nina-password")


def test_register_creates_customer_that_can_sign_in(auth_service: AuthService, account_repository: AccountRepository) -> None:
    account = auth_service.register_account(make_registration())

    assert type(account) is CustomerAccount
    assert len(account.id) == 8
    assert "password_hash" not in account.model_dump()
    assert verify_password("nina-password", account_repository.get_by_id(account.id).password_hash)
    assert sign_in(auth_service, "nina@example.com", "nina-password")


def test_register_can_create_an_owner(auth_service: AuthService) -> None:
    account = auth_service.register_account(make_registration(), role="restaurant_owner")

    assert type(account) is RestaurantAccount


@pytest.mark.parametrize("email", ["cara@example.com", " CARA@Example.com "])
def test_register_rejects_an_existing_email(auth_service: AuthService, email: str) -> None:
    with pytest.raises(EmailAlreadyRegisteredError):
        auth_service.register_account(make_registration(email))


def test_get_account_returns_public_account(auth_service: AuthService) -> None:
    account = auth_service.get_account("cust_001")

    assert type(account) is CustomerAccount
    assert "password_hash" not in account.model_dump()


@pytest.mark.parametrize("method", ["get_account", "deactivate_account"])
def test_unknown_account_raises(auth_service: AuthService, method: str) -> None:
    with pytest.raises(AccountNotFoundError):
        getattr(auth_service, method)("nope_000")
