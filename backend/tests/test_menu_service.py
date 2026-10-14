import json

from pydantic import ValidationError
from pytest import raises

from backend.app.models.menu_Item_model import CreateMenuItem, MenuItem
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.services.menu_service import MenuService


def test_add_menu_service(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"
    test_file.write_text("[]", encoding="utf-8")

    repository = MenuRepository(test_file)
    service = MenuService(repository)

    data = CreateMenuItem(
        name="Pho",
        category="Noodles",
        price=14.99,
        is_available=True,
    )

    item = service.add_menu("rest_001", data)

    assert isinstance(item, MenuItem)
    assert len(item.id) == 8
    assert item.restaurant_id == "rest_001"
    assert item.name == "Pho"
    assert item.category == "Noodles"
    assert item.price == 14.99
    assert item.is_available is True

    saved = json.loads(test_file.read_text(encoding="utf-8"))

    assert len(saved) == 1
    assert saved[0] == item.model_dump()

def test_add_menu_service_creates_different_ids(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"
    test_file.write_text("[]", encoding="utf-8")

    repository = MenuRepository(test_file)
    service = MenuService(repository)

    data = CreateMenuItem(
        name="Pho",
        category="Noodles",
        price=14.99,
        is_available=True,
    )

    first = service.add_menu("rest_001", data)
    second = service.add_menu("rest_001", data)

    assert first.id != second.id
    assert len(repository.get_all()) == 2

def test_add_menu_service_invalid_restaurant_id(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"
    test_file.write_text("[]", encoding="utf-8")

    repository = MenuRepository(test_file)
    service = MenuService(repository)

    data = CreateMenuItem(
        name="Pho",
        category="Noodles",
        price=14.99,
        is_available=True,
    )

    with raises(ValidationError):
        service.add_menu("rest_1", data)

    assert repository.get_all() == []

def test_get_menu_service(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"

    _menus = [
        {
            "id": "menu_001",
            "restaurant_id": "rest_001",
            "name": "Cheese Burger",
            "category": "Mains",
            "price": 15.99,
            "is_available": True
        },
        {
            "id": "menu_002",
            "restaurant_id": "rest_001",
            "name": "French Fries",
            "category": "Sides",
            "price": 4.99,
            "is_available": True
        }
    ]

    test_file.write_text(
        json.dumps(_menus),
        encoding="utf-8",
    )

    repository = MenuRepository(test_file)
    service = MenuService(repository)

    data = service.get_menu()

    assert isinstance(data, list)
    assert all(isinstance(item, MenuItem) for item in data)

    assert data[0].id == "menu_001"
    assert data[0].name == "Cheese Burger"
    assert data[1].id == "menu_002"
    assert data[1].name == "French Fries"

def test_get_menu_service_price_fail(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"

    _menus = [
        {
            "id": "menu_001",
            "restaurant_id": "rest_001",
            "name": "Cheese Burger",
            "category": "Mains",
            "price": 0,
            "is_available": True
        }
    ]

    test_file.write_text(
        json.dumps(_menus),
        encoding="utf-8",
    )

    repository = MenuRepository(test_file)
    service = MenuService(repository)

    with raises(ValidationError):
        service.get_menu()
