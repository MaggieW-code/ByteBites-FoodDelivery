from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from backend.app.models.cart_model import CartStatus
from backend.app.repositories.cart_repository import CartRepository
from backend.app.repositories.order_repository import OrderRepository
from backend.app.services.accounts.password_hashing import hash_password
from backend.tests.auth.auth_helpers import TEST_PASSWORD
from main import app


@pytest.fixture(scope="module")
def account_password_hash():
    return hash_password(TEST_PASSWORD)


@pytest.fixture
def order_flow(tmp_path, monkeypatch, write_json, account_password_hash):
    accounts = [
        {
            "id": account_id,
            "full_name": name,
            "email": email,
            "phone": "250-555-0100",
            "role": role,
            "is_active": True,
            "password_hash": account_password_hash,
        }
        for account_id, name, email, role in (
            ("alice001", "Alice Customer", "alice@example.com", "customer"),
            ("bob__001", "Bob Customer", "bob@example.com", "customer"),
            ("owner001", "Restaurant Owner", "owner@example.com", "restaurant_owner"),
        )
    ]
    restaurants = [{"id": "rest_001", "is_active": True}]
    menus = [
        {
            "restaurant_id": "rest_001",
            "currency": "CAD",
            "items": [
                {"id": "item_001", "name": "Burger", "description": "", "price": "13.75", "is_available": True},
            ],
        },
    ]
    carts_path = tmp_path / "carts.json"
    orders_path = tmp_path / "orders.json"
    monkeypatch.setenv("ACCOUNTS_PATH", str(write_json("accounts.json", accounts)))
    monkeypatch.setenv("SESSIONS_PATH", str(tmp_path / "sessions.json"))
    monkeypatch.setenv("RESTAURANT_TRIAL_PATH", str(write_json("restaurants.json", restaurants)))
    monkeypatch.setenv("MENUS_PATH", str(write_json("menus.json", menus)))
    monkeypatch.setenv("CARTS_PATH", str(carts_path))
    monkeypatch.setenv("ORDERS_PATH", str(orders_path))

    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, CartRepository(carts_path), OrderRepository(orders_path)


def sign_in(client, email="alice@example.com"):
    response = client.post("/auth/sign-in", json={"email": email, "password": TEST_PASSWORD})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def fill_cart(client, headers):
    response = client.post(
        "/cart/items?restaurant_id=rest_001",
        headers=headers,
        json={"menu_item_id": "item_001", "quantity": 2},
    )
    assert response.status_code == 200
    return response.json()["id"]


def test_signed_in_customer_can_check_out_and_retrieve_order(order_flow):
    client, carts, orders = order_flow
    headers = sign_in(client)
    cart_id = fill_cart(client, headers)

    response = client.post("/checkout", headers=headers, json={"cart_id": cart_id})

    assert response.status_code == 201
    order = response.json()
    assert order["customer_id"] == "alice001"
    assert order["total"] == "27.50"
    assert carts.get_by_id(cart_id).status == CartStatus.CHECKED_OUT
    assert orders.get_by_id(order["order_id"]).model_dump(mode="json") == order
    assert client.get(f"/orders/{order['order_id']}", headers=headers).json() == order
    assert client.get("/customers/alice001/orders", headers=headers).json() == [order]
    assert client.get("/cart", headers=headers).json()["id"] != cart_id

    assert client.post("/auth/sign-out", headers=headers).status_code == 204
    assert client.get(f"/orders/{order['order_id']}", headers=headers).status_code == 401


def test_verified_identity_controls_cart_checkout_and_order_access(order_flow):
    client, _, _ = order_flow
    alice = sign_in(client)
    bob = sign_in(client, "bob@example.com")
    owner = sign_in(client, "owner@example.com")
    cart_id = fill_cart(client, alice)

    assert client.post("/checkout", headers=bob, json={"cart_id": cart_id}).status_code == 404
    assert client.post("/checkout", headers=owner, json={"cart_id": cart_id}).status_code == 403
    assert client.get("/cart", headers=owner).status_code == 403

    created = client.post("/checkout", headers=alice, json={"cart_id": cart_id})
    assert created.status_code == 201
    order_path = f"/orders/{created.json()['order_id']}"
    assert client.get(order_path, headers=bob).status_code == 404
    assert client.get(order_path, headers=owner).status_code == 403
    assert client.get("/customers/alice001/orders", headers=bob).status_code == 403


def test_checkout_persistence_failure_leaves_cart_active(order_flow, monkeypatch):
    client, carts, orders = order_flow
    headers = sign_in(client)
    cart_id = fill_cart(client, headers)

    def fail_save(_repository, _order):
        raise OSError("Order storage is unavailable")

    with monkeypatch.context() as storage_failure:
        storage_failure.setattr(OrderRepository, "save", fail_save)
        response = client.post("/checkout", headers=headers, json={"cart_id": cart_id})

    assert response.status_code == 500
    assert carts.get_by_id(cart_id).status == CartStatus.ACTIVE
    assert orders.get_all() == []
    assert client.post("/checkout", headers=headers, json={"cart_id": cart_id}).status_code == 201


def test_concurrent_checkout_requests_reuse_the_saved_order(order_flow):
    client, carts, orders = order_flow
    headers = sign_in(client)
    cart_id = fill_cart(client, headers)

    def checkout():
        return client.post("/checkout", headers=headers, json={"cart_id": cart_id})

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(checkout)
        second = executor.submit(checkout)
        responses = [first.result(), second.result()]

    assert [response.status_code for response in responses] == [201, 201]
    assert responses[0].json() == responses[1].json()
    assert len(orders.get_all()) == 1
    assert carts.get_by_id(cart_id).status == CartStatus.CHECKED_OUT



def test_checkout_menu_read_error_leaves_cart_active(order_flow, tmp_path):
    client, carts, orders = order_flow
    headers = sign_in(client)
    cart_id = fill_cart(client, headers)
    (tmp_path / "menus.json").write_text("{", encoding="utf-8")

    response = client.post("/checkout", headers=headers, json={"cart_id": cart_id})

    assert response.status_code == 409
    assert response.json() == {"detail": "Restaurant menu is invalid"}
    assert carts.get_by_id(cart_id).status == CartStatus.ACTIVE
    assert orders.get_all() == []
