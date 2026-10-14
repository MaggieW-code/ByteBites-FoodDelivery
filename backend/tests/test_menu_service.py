import json

from pydantic import ValidationError
from pytest import raises

from backend.app.models.menu_Item_model import CreateMenuItem, MenuItem
from backend.app.models.update_menu_item_model import UpdateMenuItem
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.services.menu_service import MenuItemNotFoundError, MenuService


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

def _write_update_test_menus(test_file) -> list[dict]:
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

    return _menus

def test_update_menu_service_only_price(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"
    _menus = _write_update_test_menus(test_file)

    repository = MenuRepository(test_file)
    service = MenuService(repository)

    updated = service.update_menu("rest_001", "menu_002", UpdateMenuItem(price=3.99))

    assert isinstance(updated, MenuItem)
    assert updated.id == "menu_002"
    assert updated.restaurant_id == "rest_001"
    assert updated.price == 3.99
    assert updated.name == "French Fries"
    assert updated.category == "Sides"
    assert updated.is_available is True

    saved = repository.get_all()

    assert saved[0] == _menus[0]
    assert saved[1] == updated.model_dump()

def test_update_menu_service_all_fields(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"
    _write_update_test_menus(test_file)

    repository = MenuRepository(test_file)
    service = MenuService(repository)

    data = UpdateMenuItem(
        name="Curly Fries",
        category="Snacks",
        price=5.49,
        is_available=False,
    )

    updated = service.update_menu("rest_001", "menu_002", data)

    assert updated.name == "Curly Fries"
    assert updated.category == "Snacks"
    assert updated.price == 5.49
    assert updated.is_available is False
    assert updated.id == "menu_002"
    assert updated.restaurant_id == "rest_001"

def test_update_menu_service_no_fields_changes_nothing(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"
    _menus = _write_update_test_menus(test_file)

    repository = MenuRepository(test_file)
    service = MenuService(repository)

    updated = service.update_menu("rest_001", "menu_002", UpdateMenuItem())

    assert updated.model_dump() == MenuItem(**_menus[1]).model_dump()
    assert repository.get_all() == _menus

def test_update_menu_service_unknown_item(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"
    _menus = _write_update_test_menus(test_file)

    repository = MenuRepository(test_file)
    service = MenuService(repository)

    with raises(MenuItemNotFoundError):
        service.update_menu("rest_001", "menu_999", UpdateMenuItem(price=3.99))

    assert repository.get_all() == _menus

def test_update_menu_service_wrong_restaurant(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"
    _menus = _write_update_test_menus(test_file)

    repository = MenuRepository(test_file)
    service = MenuService(repository)

    with raises(MenuItemNotFoundError):
        service.update_menu("rest_002", "menu_002", UpdateMenuItem(price=3.99))

    assert repository.get_all() == _menus

def test_update_menu_service_shows_in_get_menu(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"
    _write_update_test_menus(test_file)

    repository = MenuRepository(test_file)
    service = MenuService(repository)

    service.update_menu("rest_001", "menu_002", UpdateMenuItem(price=3.99))

    menu = service.get_menu()

    assert menu[1].id == "menu_002"
    assert menu[1].price == 3.99
