import json
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from backend.app.dependencies.auth import get_account_service, get_auth_service
from backend.app.repositories.cart_repository import CartRepository
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.routes.cart_routes import get_cart_service
from backend.app.services.accounts.password_hashing import hash_password
from backend.app.services.cart_service import CartService, CartValidationError
from backend.app.services.menu_service import MenuService
from main import app


@pytest.fixture
def cart_api(tmp_path, monkeypatch):
    restaurant_path = tmp_path / "restaurants.json"
    restaurant_path.write_text(
        json.dumps([
            {"id": "rest_001", "is_active": True},
            {"id": "rest_002", "is_active": True},
        ]),
        encoding="utf-8",
    )
    menu_path = tmp_path / "menus.json"
    menu_path.write_text(json.dumps([
        {
            "restaurant_id": "rest_001",
            "currency": "CAD",
            "items": [
                {"id": "item_001", "name": "item_001", "description": "", "price": "2.50", "is_available": True},
                {"id": "item_002", "name": "item_002", "description": "", "price": "3.00", "is_available": False},
            ],
        },
        {
            "restaurant_id": "rest_002",
            "currency": "CAD",
            "items": [{"id": "item_003", "name": "item_003", "description": "", "price": "4.00", "is_available": True}],
        },
    ]), encoding="utf-8")
    repository = CartRepository(tmp_path / "carts.json")
    service = CartService(
        repository, MenuService(MenuRepository(menu_path), RestaurantRepository(restaurant_path))
    )
    monkeypatch.setitem(app.dependency_overrides, get_cart_service, lambda: service)
    with TestClient(app) as client:
        yield client, repository


CART_TEST_PASSWORD = "Cart-test-password"


@pytest.fixture(scope="session")
def cart_password_hash():
    return hash_password(CART_TEST_PASSWORD)


@pytest.fixture
def cart_accounts(tmp_path, monkeypatch, cart_password_hash):
    accounts_path = tmp_path / "cart-accounts.json"
    accounts_path.write_text(json.dumps([
        {
            "id": account_id,
            "full_name": name,
            "email": email,
            "phone": "250-555-0100",
            "role": role,
            "is_active": True,
            "password_hash": cart_password_hash,
        }
        for account_id, name, email, role in [
            ("cust_001", "Alice Customer", "alice@example.com", "customer"),
            ("cust_002", "Bob Customer", "bob@example.com", "customer"),
            ("admn_001", "Admin User", "admin@example.com", "admin"),
        ]
    ]), encoding="utf-8")
    monkeypatch.setenv("ACCOUNTS_PATH", str(accounts_path))
    monkeypatch.setenv("SESSIONS_PATH", str(tmp_path / "cart-sessions.json"))


def bearer_headers(client, email):
    response = client.post("/auth/sign-in", json={"email": email, "password": CART_TEST_PASSWORD})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def authenticated_api(cart_api, cart_accounts):
    client, _ = cart_api
    client.headers.update(bearer_headers(client, "alice@example.com"))
    return cart_api


def test_cart_lifecycle_and_response_schema(authenticated_api):
    client, _ = authenticated_api
    response = client.post("/cart")
    assert response.status_code == 200
    empty_cart = response.json()
    assert empty_cart == {
        "id": empty_cart["id"],
        "customer_id": "cust_001",
        "restaurant_id": None,
        "items": [],
        "status": "active",
        "subtotal": "0.00",
        "total": "0.00",
    }
    assert client.post("/cart").json() == empty_cart

    response = client.post(
        "/cart/items?restaurant_id=rest_001",
        json={"menu_item_id": "item_001", "quantity": 2, "price": 0, "total": 0},
    )
    assert response.status_code == 200
    filled_cart = response.json()
    assert filled_cart == {
        **empty_cart,
        "restaurant_id": "rest_001",
        "items": [{"menu_item_id": "item_001", "quantity": 2}],
        "subtotal": "5.00",
        "total": "5.00",
    }
    response = client.get("/cart")
    assert response.status_code == 200
    assert response.json() == filled_cart

    response = client.patch("/cart/items/item_001", json={"quantity": 3})
    assert response.status_code == 200
    assert response.json()["items"] == [{"menu_item_id": "item_001", "quantity": 3}]
    assert response.json()["total"] == "7.50"

    response = client.delete("/cart/items/item_001")
    assert response.status_code == 200
    assert response.json() == empty_cart

    client.post("/cart/items?restaurant_id=rest_001", json={"menu_item_id": "item_001", "quantity": 1})
    response = client.delete("/cart")
    assert response.status_code == 200
    assert response.json() == empty_cart


@pytest.mark.parametrize(("method", "url", "body"), [
    ("GET", "/cart", None),
    ("POST", "/cart", None),
    ("POST", "/cart/items?restaurant_id=rest_001", {"menu_item_id": "item_001", "quantity": 1}),
    ("PATCH", "/cart/items/item_001", {"quantity": 1}),
    ("DELETE", "/cart/items/item_001", None),
    ("DELETE", "/cart", None),
])
def test_cart_routes_require_authenticated_customer(cart_api, method, url, body):
    client, repository = cart_api
    response = client.request(method, url, json=body, headers={"X-Customer-ID": "alice"})
    assert response.status_code == 401
    assert repository.get_all() == []


def test_get_cart_is_scoped_to_authenticated_customer(authenticated_api):
    client, _ = authenticated_api
    response = client.post(
        "/cart/items?restaurant_id=rest_001", json={"menu_item_id": "item_001", "quantity": 1}
    )
    assert response.status_code == 200
    alice_cart = response.json()

    bob_headers = bearer_headers(client, "bob@example.com")
    response = client.get(
        "/cart", params={"customer_id": "cust_001"}, headers={**bob_headers, "X-Customer-ID": "cust_001"}
    )
    assert response.status_code == 200
    assert response.json()["customer_id"] == "cust_002"
    assert response.json()["id"] != alice_cart["id"]
    assert response.json()["items"] == []
    assert client.delete("/cart/items/item_001", headers=bob_headers).status_code == 404

    response = client.post(
        "/cart/items",
        params={"restaurant_id": "rest_001", "customer_id": "cust_001"},
        json={"menu_item_id": "item_001", "quantity": 5, "customer_id": "cust_001"},
        headers=bob_headers,
    )
    assert response.status_code == 200
    assert response.json()["customer_id"] == "cust_002"
    assert client.get("/cart").json() == alice_cart


def test_non_customer_cannot_open_cart(cart_api, cart_accounts):
    client, repository = cart_api
    response = client.post("/cart", headers=bearer_headers(client, "admin@example.com"))
    assert response.status_code == 403
    assert repository.get_all() == []


def test_deactivated_customer_cannot_open_cart(authenticated_api):
    client, repository = authenticated_api
    get_account_service().deactivate_account("cust_001")
    assert client.post("/cart").status_code == 401
    assert repository.get_all() == []


def test_expired_bearer_credential_cannot_open_cart(cart_api, cart_accounts, monkeypatch):
    client, repository = cart_api
    auth_service = get_auth_service()
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(auth_service, "clock", lambda: now)
    monkeypatch.setitem(app.dependency_overrides, get_auth_service, lambda: auth_service)
    headers = bearer_headers(client, "alice@example.com")

    now += auth_service.token_lifetime
    response = client.get("/cart", headers=headers)
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert repository.get_all() == []


def test_unverified_bearer_credential_cannot_open_cart(cart_api, cart_accounts):
    client, repository = cart_api
    response = client.get("/cart", headers={"Authorization": "Bearer unverified"})
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert repository.get_all() == []


@pytest.mark.parametrize(("method", "url", "body"), [
    ("POST", "/cart/items", {"menu_item_id": "item_001", "quantity": 1}),
    ("POST", "/cart/items?restaurant_id=bad", {"menu_item_id": "item_001", "quantity": 1}),
    ("POST", "/cart/items?restaurant_id=rest_001", {"menu_item_id": "short", "quantity": 1}),
    ("POST", "/cart/items?restaurant_id=rest_001", {"menu_item_id": "item_001", "quantity": 0}),
    ("PATCH", "/cart/items/item_001", {"quantity": "2"}),
    ("DELETE", "/cart/items/short", None),
])
def test_invalid_cart_requests_return_422(authenticated_api, method, url, body):
    client, repository = authenticated_api
    response = client.request(method, url, json=body)
    assert response.status_code == 422
    assert repository.get_all() == []


def test_missing_items_and_conflicts(authenticated_api):
    client, _ = authenticated_api
    assert client.patch("/cart/items/item_001", json={"quantity": 2}).status_code == 404

    response = client.post(
        "/cart/items?restaurant_id=rest_001", json={"menu_item_id": "unknown_", "quantity": 1}
    )
    assert response.status_code == 404

    response = client.post(
        "/cart/items?restaurant_id=rest_999", json={"menu_item_id": "item_001", "quantity": 1}
    )
    assert response.status_code == 404

    response = client.post(
        "/cart/items?restaurant_id=rest_001", json={"menu_item_id": "item_002", "quantity": 1}
    )
    assert response.status_code == 409

    response = client.post(
        "/cart/items?restaurant_id=rest_001", json={"menu_item_id": "item_001", "quantity": 1}
    )
    assert response.status_code == 200
    cart = response.json()
    response = client.post(
        "/cart/items?restaurant_id=rest_002", json={"menu_item_id": "item_003", "quantity": 1}
    )
    assert response.status_code == 409
    assert client.get("/cart").json() == cart


def test_inactive_restaurant_blocks_additions_but_existing_cart_can_be_cleared(
    authenticated_api, tmp_path
):
    client, repository = authenticated_api
    url = "/cart/items?restaurant_id=rest_002"
    item = {"menu_item_id": "item_003", "quantity": 1}
    initial = client.post(url, json=item)
    assert initial.status_code == 200

    restaurant_path = tmp_path / "restaurants.json"
    restaurants = json.loads(restaurant_path.read_text(encoding="utf-8"))
    restaurants[1]["is_active"] = False
    restaurant_path.write_text(json.dumps(restaurants), encoding="utf-8")

    response = client.post(url, json=item)
    assert response.status_code == 409
    assert response.json()["detail"] == "Restaurant 'rest_002' is inactive"
    assert repository.get_all()[0].items[0].quantity == 1
    assert client.get("/cart").json() == initial.json()
    cleared = client.delete("/cart")
    assert cleared.status_code == 200
    assert cleared.json()["items"] == []


def test_service_validation_error_mapping(authenticated_api, monkeypatch):
    client, _ = authenticated_api

    def reject_customer(customer_id):
        raise CartValidationError("Invalid customer")

    monkeypatch.setattr(app.dependency_overrides[get_cart_service](), "get_cart", reject_customer)
    response = client.get("/cart")
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid customer"}


def test_cart_storage_error_hides_internal_details(authenticated_api):
    client, repository = authenticated_api
    repository.data_path.write_text("{", encoding="utf-8")
    response = client.get("/cart")
    assert response.status_code == 500
    assert response.json() == {"detail": "Unable to access cart data"}


def test_frontend_can_preflight_cart_delete(cart_api):
    client, _ = cart_api
    response = client.options("/cart", headers={
        "Origin": "http://localhost:1234",
        "Access-Control-Request-Method": "DELETE",
        "Access-Control-Request-Headers": "Authorization",
    })
    assert response.status_code == 200
    assert "DELETE" in response.headers["Access-Control-Allow-Methods"]
    assert "Authorization" in response.headers["Access-Control-Allow-Headers"]
