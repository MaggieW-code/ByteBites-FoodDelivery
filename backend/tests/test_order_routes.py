import pytest
from fastapi.testclient import TestClient

from backend.app.repositories.order_repository import OrderRepository
from backend.app.routes.order_routes import get_authenticated_order_customer_id, get_order_service
from backend.app.services.order_service import OrderService
from backend.tests.test_order_repository import make_order
from main import app


@pytest.fixture
def order_api(tmp_path, monkeypatch):
    repository = OrderRepository(tmp_path / "orders.json")
    monkeypatch.setitem(app.dependency_overrides, get_order_service, lambda: OrderService(repository))
    with TestClient(app) as client:
        yield client, repository


@pytest.fixture
def customer_api(order_api, monkeypatch):
    monkeypatch.setitem(
        app.dependency_overrides, get_authenticated_order_customer_id, lambda: "customer_001"
    )
    return order_api


@pytest.mark.parametrize("path", ["/orders/order_001", "/customers/customer_001/orders"])
def test_order_endpoints_require_authentication_even_with_claimed_customer(order_api, path):
    client, repository = order_api
    repository.save(make_order())

    response = client.get(path, headers={"X-Customer-ID": "customer_001"})

    assert response.status_code == 401


def test_order_detail_preserves_purchase_snapshot(customer_api):
    client, repository = customer_api
    order = repository.save(make_order())

    response = client.get(f"/orders/{order.order_id}")

    assert response.status_code == 200
    assert response.json() == order.model_dump(mode="json")
    assert response.json()["items"][0]["unit_price"] == "12.50"


def test_order_history_returns_only_owned_orders(customer_api):
    client, repository = customer_api
    owned = [repository.save(make_order(order_id)) for order_id in ("first", "second")]
    repository.save(make_order("foreign", "customer_002"))

    response = client.get("/customers/customer_001/orders")

    assert response.status_code == 200
    assert response.json() == [order.model_dump(mode="json") for order in owned]


def test_empty_order_history_returns_empty_list(customer_api):
    client, _ = customer_api

    response = client.get("/customers/customer_001/orders")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize("order_id", ["missing", "foreign"])
def test_missing_and_foreign_order_details_return_404(customer_api, order_id):
    client, repository = customer_api
    repository.save(make_order("foreign", "customer_002"))

    response = client.get(f"/orders/{order_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Order not found"}


def test_foreign_order_history_returns_403(customer_api):
    client, _ = customer_api

    assert client.get("/customers/customer_002/orders").status_code == 403


def test_order_endpoints_are_documented(order_api):
    client, _ = order_api
    paths = client.get("/openapi.json").json()["paths"]

    assert {"200", "401", "403", "404"} <= paths["/orders/{order_id}"]["get"]["responses"].keys()
    assert {"200", "401", "403"} <= paths["/customers/{customer_id}/orders"]["get"]["responses"].keys()
