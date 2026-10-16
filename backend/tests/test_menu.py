import json

import pytest
from fastapi.testclient import TestClient

from backend.app.models.menu_model import Menu
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.routes import menu_routes
from backend.app.services.menu_service import MenuRestaurantNotFoundError, MenuService
from main import app


@pytest.fixture
def menu_data():
    return [dict(restaurant_id="rest_001", currency="CAD", items=[
        dict(id="dish_001", name="Soup", description="Vegetable soup", price="8.50", is_available=True),
        dict(id="dish_002", name="Salad", description="Green salad", price="6.00", is_available=False),
    ]), dict(restaurant_id="rest_002", currency="CAD", items=[
        dict(id="dish_003", name="Pasta", description="Tomato pasta", price="12.00", is_available=True),
    ])]


@pytest.fixture
def service(tmp_path, menu_data):
    menus = tmp_path / "menus.json"
    menus.write_text(json.dumps(menu_data), encoding="utf-8")
    restaurants = tmp_path / "restaurants.json"
    restaurants.write_text(json.dumps([{"id": f"rest_{i:03}"} for i in range(1, 4)]), encoding="utf-8")
    return MenuService(MenuRepository(menus), RestaurantRepository(restaurants))


@pytest.fixture
def client(service, monkeypatch):
    monkeypatch.setattr(menu_routes, "menu_service", service)
    with TestClient(app) as client:
        yield client


def test_repository_isolates_restaurant_items_and_reloads_persistence(service):
    repository = MenuRepository(service.menu_repository.data_path)
    assert [item["name"] for item in repository.get_by_restaurant_id("rest_002")["items"]] == ["Pasta"]
    assert repository.get_by_restaurant_id("rest_999") is None


def test_service_returns_model_and_empty_menu(service):
    assert isinstance(service.get_menu("rest_001"), Menu)
    assert service.get_menu("rest_003").items == []


def test_service_unknown_restaurant(service):
    with pytest.raises(MenuRestaurantNotFoundError):
        service.get_menu("rest_999")


def test_api_returns_selected_menu(client, menu_data):
    response = client.get("/restaurants/rest_001/menu")
    assert response.status_code == 200
    assert response.json() == menu_data[0]
    assert client.get("/restaurants/rest_002/menu").json() == menu_data[1]


def test_api_empty_menu(client):
    assert client.get("/restaurants/rest_003/menu").json() == {
        "restaurant_id": "rest_003", "currency": "CAD", "items": []}


def test_api_unknown_restaurant(client):
    response = client.get("/restaurants/rest_999/menu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

