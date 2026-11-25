"""The /customers routes on the real app (epic #114)."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.app.repositories.accounts.account_repository import AccountRepository
from backend.app.services.accounts.password_hashing import verify_password


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
