"""The /customers routes on the real app (epic #114)."""

from collections.abc import Callable
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.app.repositories.accounts.account_repository import AccountRepository
from backend.app.services.accounts.password_hashing import verify_password
from backend.tests.auth.auth_helpers import TEST_PASSWORD

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
    client: TestClient, auth_headers: AuthHeaders, deactivate_in_storage: Callable[[str], None]
) -> None:
    headers = auth_headers("cara@example.com")
    deactivate_in_storage("cust_001")

    assert client.get("/customers/me", headers=headers).status_code == 403


# --- C4: update ---


def test_customer_updates_their_profile(client: TestClient, auth_headers: AuthHeaders) -> None:
    headers = auth_headers("cara@example.com")
    body = {
        "full_name": "Cara Renamed",
        "email": "cara.new@example.com",
        "phone": "(250) 555-0199",
    }

    response = client.patch("/customers/me", headers=headers, json=body)

    assert response.status_code == 200
    assert response.json() == {
        "id": "cust_001",
        "full_name": "Cara Renamed",
        "email": "cara.new@example.com",
        "phone": "+12505550199",
        "is_active": True,
        "role": "customer",
        "delivery_addresses": [],
    }
    assert client.get("/customers/me", headers=headers).json() == response.json()


def test_update_ignores_fields_a_customer_cannot_change(client: TestClient, auth_headers: AuthHeaders) -> None:
    body = {
        "full_name": "Cara",
        "role": "admin",
        "is_active": False,
        "id": "hack_001",
        "password": "new-password",
        "delivery_addresses": [{"id": "addr_001", "label": "Home", "address": "1 Main St"}],
    }

    customer = client.patch("/customers/me", headers=auth_headers("cara@example.com"), json=body).json()

    assert (customer["id"], customer["role"], customer["is_active"]) == ("cust_001", "customer", True)
    assert customer["delivery_addresses"] == []
    sign_in = client.post("/auth/sign-in", json={"email": "cara@example.com", "password": TEST_PASSWORD})
    assert sign_in.status_code == 200


def test_update_to_another_accounts_email_is_409(client: TestClient, auth_headers: AuthHeaders) -> None:
    response = client.patch("/customers/me", headers=auth_headers("cara@example.com"), json={"email": "omar@example.com"})

    assert response.status_code == 409


@pytest.mark.parametrize(
    "body",
    [{}, {"full_name": None}, {"email": "not-an-email"}, {"phone": "12501233211"}],
    ids=["empty", "null-name", "bad-email", "bad-phone"],
)
def test_invalid_update_is_422_and_saves_nothing(
    client: TestClient, auth_headers: AuthHeaders, account_repository: AccountRepository, body: dict[str, Any]
) -> None:
    before = account_repository.load_all()

    response = client.patch("/customers/me", headers=auth_headers("cara@example.com"), json=body)

    assert response.status_code == 422
    assert account_repository.load_all() == before


def test_update_without_a_token_is_401(client: TestClient) -> None:
    assert client.patch("/customers/me", json={"full_name": "Nobody"}).status_code == 401


def test_update_by_a_non_customer_is_403(client: TestClient, auth_headers: AuthHeaders) -> None:
    response = client.patch("/customers/me", headers=auth_headers("omar@example.com"), json={"full_name": "Omar"})

    assert response.status_code == 403


# --- C4: delivery addresses ---

HOME = {"label": "Home", "address": "1 Main St"}
WORK = {"label": "Work", "address": "2 Office Rd"}


def test_add_address_returns_201_with_an_id_and_keeps_earlier_ones(client: TestClient, auth_headers: AuthHeaders) -> None:
    headers = auth_headers("cara@example.com")

    home = client.post("/customers/me/addresses", headers=headers, json=HOME)
    work = client.post("/customers/me/addresses", headers=headers, json=WORK)

    assert (home.status_code, work.status_code) == (201, 201)
    assert home.json() == {"id": home.json()["id"], **HOME}
    assert client.get("/customers/me", headers=headers).json()["delivery_addresses"] == [home.json(), work.json()]


def test_edit_and_remove_one_address(client: TestClient, auth_headers: AuthHeaders) -> None:
    headers = auth_headers("cara@example.com")
    home = client.post("/customers/me/addresses", headers=headers, json=HOME).json()
    work = client.post("/customers/me/addresses", headers=headers, json=WORK).json()

    edited = client.patch(f"/customers/me/addresses/{home['id']}", headers=headers, json={"address": "9 New Ave"})
    assert edited.status_code == 200
    assert edited.json() == {"id": home["id"], "label": "Home", "address": "9 New Ave"}

    assert client.delete(f"/customers/me/addresses/{work['id']}", headers=headers).status_code == 204
    assert client.get("/customers/me", headers=headers).json()["delivery_addresses"] == [edited.json()]


@pytest.mark.parametrize("method", ["patch", "delete"])
def test_unknown_address_is_404(client: TestClient, auth_headers: AuthHeaders, method: str) -> None:
    extra = {"json": {"label": "X"}} if method == "patch" else {}

    response = getattr(client, method)("/customers/me/addresses/nope_000", headers=auth_headers("cara@example.com"), **extra)

    assert response.status_code == 404


def test_customers_cannot_touch_each_others_addresses(client: TestClient, auth_headers: AuthHeaders) -> None:
    cara_address = client.post("/customers/me/addresses", headers=auth_headers("cara@example.com"), json=HOME).json()
    client.post("/customers", json=registration_body(password=TEST_PASSWORD))
    nina = auth_headers("nina@example.com")

    assert client.delete(f"/customers/me/addresses/{cara_address['id']}", headers=nina).status_code == 404
    assert client.get("/customers/me", headers=auth_headers("cara@example.com")).json()["delivery_addresses"] == [cara_address]


@pytest.mark.parametrize(
    "path, method, body",
    [
        ("/customers/me/addresses", "post", {"label": "Home"}),
        ("/customers/me/addresses", "post", {"label": "", "address": "1 Main St"}),
        ("/customers/me/addresses/addr_001", "patch", {}),
        ("/customers/me/addresses/short", "patch", {"label": "X"}),
    ],
    ids=["missing-address", "empty-label", "empty-update", "bad-address-id"],
)
def test_invalid_address_request_is_422(
    client: TestClient, auth_headers: AuthHeaders, path: str, method: str, body: dict[str, Any]
) -> None:
    response = getattr(client, method)(path, headers=auth_headers("cara@example.com"), json=body)

    assert response.status_code == 422


@pytest.mark.parametrize(
    "method, path",
    [
        ("post", "/customers/me/addresses"),
        ("patch", "/customers/me/addresses/addr_001"),
        ("delete", "/customers/me/addresses/addr_001"),
    ],
    ids=["add", "edit", "remove"],
)
def test_address_routes_need_a_customer(client: TestClient, auth_headers: AuthHeaders, method: str, path: str) -> None:
    extra = {} if method == "delete" else {"json": HOME}

    assert getattr(client, method)(path, **extra).status_code == 401
    assert getattr(client, method)(path, headers=auth_headers("omar@example.com"), **extra).status_code == 403


# --- C5: deactivate ---


def test_deactivate_returns_204_and_signs_the_customer_out_everywhere(client: TestClient, auth_headers: AuthHeaders) -> None:
    laptop = auth_headers("cara@example.com")
    phone = auth_headers("cara@example.com")

    assert client.post("/customers/me/deactivate", headers=laptop).status_code == 204

    assert client.get("/customers/me", headers=laptop).status_code == 401
    assert client.get("/customers/me", headers=phone).status_code == 401


def test_deactivated_customer_cannot_sign_in_again(client: TestClient, auth_headers: AuthHeaders) -> None:
    client.post("/customers/me/deactivate", headers=auth_headers("cara@example.com"))

    response = client.post("/auth/sign-in", json={"email": "cara@example.com", "password": TEST_PASSWORD})

    assert response.status_code == 403


def test_deactivating_one_customer_leaves_others_signed_in(client: TestClient, auth_headers: AuthHeaders) -> None:
    owner = auth_headers("omar@example.com")

    client.post("/customers/me/deactivate", headers=auth_headers("cara@example.com"))

    assert client.get("/auth/me", headers=owner).status_code == 200


def test_deactivate_needs_a_customer(client: TestClient, auth_headers: AuthHeaders) -> None:
    assert client.post("/customers/me/deactivate").status_code == 401
    assert client.post("/customers/me/deactivate", headers=auth_headers("omar@example.com")).status_code == 403
