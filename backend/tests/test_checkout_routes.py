from unittest.mock import create_autospec

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.app.models.order_model import Order, OrderItem
from backend.app.routes.auth_dependencies import AuthenticatedCustomer, get_current_active_customer
from backend.app.routes.checkout_routes import get_checkout_service
from backend.app.services.checkout_service import (
    CheckoutCartNotFoundError,
    CheckoutConflictError,
    CheckoutService,
    CheckoutUnavailableError,
)
from main import app

client = TestClient(app)


@pytest.fixture
def signed_in_customer(monkeypatch):
    customer = AuthenticatedCustomer(customer_id="customer_001")
    monkeypatch.setitem(app.dependency_overrides, get_current_active_customer, lambda: customer)
    return customer


@pytest.fixture
def checkout_service(monkeypatch):
    service = create_autospec(CheckoutService, instance=True)
    monkeypatch.setitem(app.dependency_overrides, get_checkout_service, lambda: service)
    return service


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer unverified"}])
def test_checkout_requires_verified_credentials(headers):
    response = client.post("/checkout", json={"cart_id": "cart_001"}, headers=headers)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_checkout_uses_authenticated_customer_id(signed_in_customer, checkout_service):
    order = Order(
        order_id="order_001",
        customer_id=signed_in_customer.customer_id,
        restaurant_id="rest_001",
        items=[OrderItem(item_id="item_001", name="Burger", quantity=2, unit_price="13.75", line_total="27.50")],
        total="27.50",
    )
    checkout_service.checkout.return_value = order

    response = client.post("/checkout", json={"cart_id": "cart_001"})

    assert response.status_code == 201
    assert response.json() == order.model_dump(mode="json")
    checkout_service.checkout.assert_called_once_with(customer_id=signed_in_customer.customer_id, cart_id="cart_001")


def test_checkout_rejects_identity_in_request_body(signed_in_customer, checkout_service):
    response = client.post("/checkout", json={"cart_id": "cart_001", "customer_id": "another_customer"})

    assert response.status_code == 422
    checkout_service.checkout.assert_not_called()


def test_checkout_preserves_auth_forbidden_response(monkeypatch, checkout_service):
    def deny_customer():
        raise HTTPException(status_code=403, detail="Active customer required")

    monkeypatch.setitem(app.dependency_overrides, get_current_active_customer, deny_customer)

    response = client.post("/checkout", json={"cart_id": "cart_001"})

    assert response.status_code == 403
    checkout_service.checkout.assert_not_called()


@pytest.mark.parametrize(
    ("error", "status_code"),
    [
        (CheckoutCartNotFoundError("Cart not found"), 404),
        (CheckoutConflictError("Cart changed"), 409),
        (CheckoutUnavailableError("Menu item is unavailable"), 409),
    ],
)
def test_checkout_translates_service_errors(signed_in_customer, checkout_service, error, status_code):
    checkout_service.checkout.side_effect = error

    response = client.post("/checkout", json={"cart_id": "cart_001"})

    assert response.status_code == status_code
    assert response.json() == {"detail": str(error)}


def test_checkout_returns_404_for_missing_cart(signed_in_customer, tmp_path, monkeypatch):
    monkeypatch.setenv("CARTS_PATH", str(tmp_path / "carts.json"))
    monkeypatch.setenv("ORDERS_PATH", str(tmp_path / "orders.json"))

    response = client.post("/checkout", json={"cart_id": "cart_001"})

    assert response.status_code == 404
