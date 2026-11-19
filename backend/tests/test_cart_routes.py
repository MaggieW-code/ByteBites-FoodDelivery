import json

import pytest
from fastapi.testclient import TestClient

from backend.app.routes.cart_routes import get_authenticated_customer_id, get_cart_service
from backend.app.repositories.cart_repository import CartRepository
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.services.cart_service import CartService, CartValidationError
from main import app


@pytest.fixture
def cart_api(tmp_path, monkeypatch):
    menu_path = tmp_path / "menus.json"
    menu_path.write_text(json.dumps([
        {
            "restaurant_id": "rest_001",
            "items": [
                {"id": "item_001", "price": "2.50", "is_available": True},
                {"id": "item_002", "price": "3.00", "is_available": False},
            ],
        },
        {
            "restaurant_id": "rest_002",
            "items": [{"id": "item_003", "price": "4.00", "is_available": True}],
        },
    ]), encoding="utf-8")
    repository = CartRepository(tmp_path / "carts.json")
    service = CartService(repository, MenuRepository(menu_path))
    monkeypatch.setitem(app.dependency_overrides, get_cart_service, lambda: service)
    with TestClient(app) as client:
        yield client, repository


@pytest.fixture
def authenticated_api(cart_api, monkeypatch):
    monkeypatch.setitem(app.dependency_overrides, get_authenticated_customer_id, lambda: "alice")
    return cart_api


def test_cart_lifecycle_and_response_schema(authenticated_api):
    client, _ = authenticated_api
    response = client.post("/cart")
    assert response.status_code == 200
    empty_cart = response.json()
    assert empty_cart == {
        "id": empty_cart["id"],
        "customer_id": "alice",
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


def test_get_cart_is_scoped_to_authenticated_customer(cart_api, monkeypatch):
    client, _ = cart_api
    customer = "alice"
    monkeypatch.setitem(app.dependency_overrides, get_authenticated_customer_id, lambda: customer)
    alice_cart = client.post(
        "/cart/items?restaurant_id=rest_001", json={"menu_item_id": "item_001", "quantity": 1}
    ).json()

    customer = "bob"
    response = client.get("/cart", params={"customer_id": "alice"}, headers={"X-Customer-ID": "alice"})
    assert response.status_code == 200
    assert response.json()["customer_id"] == "bob"
    assert response.json()["id"] != alice_cart["id"]
    assert response.json()["items"] == []
    assert client.delete("/cart/items/item_001").status_code == 404

    customer = "alice"
    assert client.get("/cart").json() == alice_cart


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
    })
    assert response.status_code == 200
    assert "DELETE" in response.headers["Access-Control-Allow-Methods"]
