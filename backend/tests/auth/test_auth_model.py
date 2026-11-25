from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pydantic import ValidationError

from backend.app.models.accounts.auth_model import AuthenticatedAccount, Session, SignInRequest, TokenResponse


@pytest.fixture
def authenticated_customer() -> AuthenticatedAccount:
    return AuthenticatedAccount(id="cust_001", role="customer", is_active=True)


@pytest.fixture
def session_fields() -> dict[str, Any]:
    created_at = datetime(2026, 11, 22, 12, 0, tzinfo=timezone.utc)
    return dict(
        token_hash="sha256-of-token",
        account_id="cust_001",
        created_at=created_at,
        expires_at=created_at + timedelta(hours=1),
    )


def test_authenticated_account_is_frozen(authenticated_customer: AuthenticatedAccount) -> None:
    with pytest.raises(ValidationError):
        authenticated_customer.role = "admin"


@pytest.mark.parametrize("is_active", ["yes", "true", 1])
def test_authenticated_account_is_strict(is_active: Any) -> None:
    with pytest.raises(ValidationError):
        AuthenticatedAccount(id="cust_001", role="customer", is_active=is_active)


def test_sign_in_request_hides_password_and_normalizes_email() -> None:
    request = SignInRequest(email="  Cara@Example.COM ", password="hunter2")

    assert "hunter2" not in repr(request)
    assert request.password.get_secret_value() == "hunter2"
    assert request.email == "cara@example.com"


def test_sign_in_request_does_not_check_email_format() -> None:
    """Format is checked when an email is registered or changed; sign-in only looks it up."""
    assert SignInRequest(email=" Old@Bytebites.TEST ", password="hunter2").email == "old@bytebites.test"


@pytest.mark.parametrize("email", ["", "x" * 255, 123], ids=["empty", "too-long", "not-text"])
def test_sign_in_request_still_rejects_empty_oversized_or_non_text_email(email: Any) -> None:
    with pytest.raises(ValidationError):
        SignInRequest(email=email, password="hunter2")


def test_session_round_trips_through_json(session_fields: dict[str, Any]) -> None:
    session = Session(**session_fields)

    assert Session.model_validate_json(session.model_dump_json()) == session


@pytest.mark.parametrize("field", ["created_at", "expires_at"])
def test_session_rejects_times_without_timezone(session_fields: dict[str, Any], field: str) -> None:
    naive_time = session_fields[field].replace(tzinfo=None)

    with pytest.raises(ValidationError):
        Session(**session_fields | {field: naive_time})


def test_token_response_is_a_bearer_token_with_aware_expiry(session_fields: dict[str, Any]) -> None:
    response = TokenResponse(access_token="abc", expires_at=session_fields["expires_at"])

    assert response.token_type == "bearer"
    with pytest.raises(ValidationError):
        TokenResponse(access_token="abc", expires_at=session_fields["expires_at"].replace(tzinfo=None))
