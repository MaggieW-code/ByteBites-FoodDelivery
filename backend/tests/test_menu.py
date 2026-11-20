import pytest

from backend.app.models.menu_model import Menu
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.services.menu_service import MenuRestaurantNotFoundError


@pytest.fixture
def menu_records():
    return [dict(restaurant_id="rest_001", currency="CAD", items=[
        dict(id="dish_001", name="Soup", description="Vegetable soup", price="8.50", is_available=True),
        dict(id="dish_002", name="Salad", description="Green salad", price="6.00", is_available=False),
    ]), dict(restaurant_id="rest_002", currency="CAD", items=[
        dict(id="dish_003", name="Pasta", description="Tomato pasta", price="12.00", is_available=True),
    ])]


def test_repository_isolates_restaurant_items_and_reloads_persistence(menu_service):
    repository = MenuRepository(menu_service.menu_repository.data_path)
    assert [item["name"] for item in repository.get_by_restaurant_id("rest_002")["items"]] == ["Pasta"]
    assert repository.get_by_restaurant_id("rest_999") is None


def test_service_returns_model_and_empty_menu(menu_service):
    assert isinstance(menu_service.get_menu("rest_001"), Menu)
    assert menu_service.get_menu("rest_003").items == []


def test_service_unknown_restaurant(menu_service):
    with pytest.raises(MenuRestaurantNotFoundError):
        menu_service.get_menu("rest_999")


def test_api_returns_selected_menu(client, menu_records):
    response = client.get("/restaurants/rest_001/menu")
    assert response.status_code == 200
    assert response.json() == menu_records[0]
    assert client.get("/restaurants/rest_002/menu").json() == menu_records[1]


def test_api_empty_menu(client):
    assert client.get("/restaurants/rest_003/menu").json() == {
        "restaurant_id": "rest_003", "currency": "CAD", "items": []}


def test_api_unknown_restaurant(client):
    response = client.get("/restaurants/rest_999/menu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

