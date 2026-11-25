"""The /auth routes on the real app: sign in, who am I, and sign out."""

from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from backend.app.models.auth_model import TokenResponse
from backend.tests.auth.auth_helpers import TEST_PASSWORD, TOKEN_LIFETIME, FakeClock

AuthHeaders = Callable[[str], dict[str, str]]


def test_sign_in_returns_a_token_that_works_on_me(client: TestClient, clock: FakeClock) -> None:
    response = client.post("/auth/sign-in", json={"email": "cara@example.com", "password": TEST_PASSWORD})

    assert response.status_code == 200
    token = TokenResponse.model_validate(response.json())
    assert token.expires_at == clock() + TOKEN_LIFETIME

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token.access_token}"})
    assert me.json()["id"] == "cust_001"


@pytest.mark.parametrize(
    "email, password",
    [("cara@example.com", "wrong-password"), ("nobody@example.com", TEST_PASSWORD)],
    ids=["wrong-password", "unknown-email"],
)
def test_bad_credentials_give_the_same_401(client: TestClient, email: str, password: str) -> None:
    response = client.post("/auth/sign-in", json={"email": email, "password": password})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_deactivated_account_cannot_sign_in(client: TestClient) -> None:
    response = client.post("/auth/sign-in", json={"email": "dana@example.com", "password": TEST_PASSWORD})

    assert response.status_code == 403


@pytest.mark.parametrize(
    "body",
    [{}, {"email": "cara@example.com"}, {"password": TEST_PASSWORD}],
    ids=["empty", "no-password", "no-email"],
)
def test_sign_in_rejects_incomplete_body(client: TestClient, body: dict[str, str]) -> None:
    assert client.post("/auth/sign-in", json=body).status_code == 422


@pytest.mark.parametrize(
    "email, role",
    [("cara@example.com", "customer"), ("omar@example.com", "restaurant_owner")],
    ids=["customer", "owner"],
)
def test_me_returns_the_callers_public_profile(client: TestClient, auth_headers: AuthHeaders, email: str, role: str) -> None:
    response = client.get("/auth/me", headers=auth_headers(email))

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == email
    assert body["role"] == role
    assert "password_hash" not in body


def test_me_without_token_is_401_with_challenge(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_sign_out_ends_the_session(client: TestClient, auth_headers: AuthHeaders) -> None:
    headers = auth_headers("cara@example.com")

    response = client.post("/auth/sign-out", headers=headers)

    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/auth/me", headers=headers).status_code == 401


def test_sign_out_with_unknown_token_is_204(client: TestClient) -> None:
    response = client.post("/auth/sign-out", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 204


def test_signing_out_twice_is_204_both_times(client: TestClient, auth_headers: AuthHeaders) -> None:
    headers = auth_headers("cara@example.com")

    first = client.post("/auth/sign-out", headers=headers)
    second = client.post("/auth/sign-out", headers=headers)

    assert (first.status_code, second.status_code) == (204, 204)


def test_sign_out_without_token_is_401_with_challenge(client: TestClient) -> None:
    response = client.post("/auth/sign-out")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_sign_out_ends_only_that_session(client: TestClient, auth_headers: AuthHeaders) -> None:
    phone = auth_headers("cara@example.com")
    laptop = auth_headers("cara@example.com")

    client.post("/auth/sign-out", headers=phone)

    assert client.get("/auth/me", headers=laptop).status_code == 200
