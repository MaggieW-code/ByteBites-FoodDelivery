"""The /customers routes on the real app (epic #114)."""

from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.app.repositories.accounts.account_repository import AccountRepository
from backend.app.services.accounts.account_service import AccountService
from backend.app.services.accounts.password_hashing import verify_password

AuthHeaders = Callable[[str], dict[str, str]]


def registration_body(**overrides: Any) -> dict[str, Any]:
    return {
        "full_name": "Nina New",
        "email": "nina@example.com",
        "phone": "(250) 555-0123",
        "password": "nina-password",
    } | overrides


# --- C1: register ---


def test_register_returns_201_with_the_public_customer(client: TestClient) -> None:
    response = client.post("/customers", json=registration_body())

    assert response.status_code == 201
    customer = response.json()
    assert len(customer["id"]) == 8
    assert customer | {"id": None} == {
        "id": None,
        "full_name": "Nina New",
        "email": "nina@example.com",
        "phone": "+12505550123",
        "is_active": True,
        "role": "customer",
        "delivery_addresses": [],
    }


def test_register_saves_the_customer_with_a_hashed_password(client: TestClient, account_repository: AccountRepository) -> None:
    customer_id = client.post("/customers", json=registration_body()).json()["id"]

    stored = account_repository.get_by_id(customer_id)
    assert stored is not None
    assert stored.password_hash != "nina-password"
    assert verify_password("nina-password", stored.password_hash)


def test_register_never_returns_the_password(client: TestClient) -> None:
    response = client.post("/customers", json=registration_body())

    assert "password" not in response.text
    assert "nina-password" not in response.text


def test_register_ignores_a_requested_role(client: TestClient) -> None:
    response = client.post("/customers", json=registration_body(role="admin"))

    assert response.status_code == 201
    assert response.json()["role"] == "customer"


@pytest.mark.parametrize("email", ["cara@example.com", " CARA@Example.com "], ids=["same", "case-and-spaces"])
def test_register_rejects_an_existing_email_with_409(client: TestClient, email: str) -> None:
    response = client.post("/customers", json=registration_body(email=email))

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered: cara@example.com"


@pytest.mark.parametrize(
    "body",
    [
        {},
        {key: value for key, value in registration_body().items() if key != "password"},
        registration_body(full_name=""),
        registration_body(phone=""),
        registration_body(password="short"),
        registration_body(email=123),
        registration_body(email="nina-at-example.com"),
        registration_body(phone="02505550123"),
    ],
    ids=["empty", "no-password", "empty-name", "empty-phone", "short-password", "email-not-text", "bad-email", "bad-phone"],
)
def test_register_rejects_an_invalid_body_with_422(client: TestClient, body: dict[str, Any]) -> None:
    assert client.post("/customers", json=body).status_code == 422


def test_rejected_registration_saves_nothing(client: TestClient, account_repository: AccountRepository) -> None:
    before = account_repository.load_all()

    client.post("/customers", json=registration_body(email="cara@example.com"))
    client.post("/customers", json=registration_body(password="short"))

    assert account_repository.load_all() == before


# --- C2: sign in ---


@pytest.mark.parametrize(
    "registered_email, sign_in_email",
    [("nina@example.com", "nina@example.com"), ("Nina@Example.com", "  NINA@example.COM ")],
    ids=["same", "case-and-spaces"],
)
def test_registered_customer_can_sign_in_and_see_their_profile(
    client: TestClient, registered_email: str, sign_in_email: str
) -> None:
    registered = client.post("/customers", json=registration_body(email=registered_email)).json()

    sign_in = client.post("/auth/sign-in", json={"email": sign_in_email, "password": "nina-password"})
    assert sign_in.status_code == 200

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {sign_in.json()['access_token']}"})
    assert me.status_code == 200
    assert me.json() == registered


def test_registered_customer_with_wrong_password_gets_401(client: TestClient) -> None:
    client.post("/customers", json=registration_body())

    response = client.post("/auth/sign-in", json={"email": "nina@example.com", "password": "not-nina-password"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


# --- C3: retrieve ---


def test_customer_gets_their_own_profile(client: TestClient, auth_headers: AuthHeaders) -> None:
    response = client.get("/customers/me", headers=auth_headers("cara@example.com"))

    assert response.status_code == 200
    assert response.json() == {
        "id": "cust_001",
        "full_name": "Cara Customer",
        "email": "cara@example.com",
        "phone": "+12505550100",
        "is_active": True,
        "role": "customer",
        "delivery_addresses": [],
    }


def test_profile_without_a_token_is_401_with_challenge(client: TestClient) -> None:
    response = client.get("/customers/me")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_profile_for_a_non_customer_is_403(client: TestClient, auth_headers: AuthHeaders) -> None:
    response = client.get("/customers/me", headers=auth_headers("omar@example.com"))

    assert response.status_code == 403


def test_profile_for_a_deactivated_customer_is_403(
    client: TestClient, auth_headers: AuthHeaders, account_service: AccountService
) -> None:
    headers = auth_headers("cara@example.com")
    account_service.deactivate_account("cust_001")

    assert client.get("/customers/me", headers=headers).status_code == 403
