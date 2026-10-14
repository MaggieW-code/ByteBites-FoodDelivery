import json

from pytest import raises

from backend.app.models.menu_Item_model import MenuItem
from backend.app.repositories.menu_repository import (
    MenuDataError,
    MenuDataMalformedError,
    MenuDataNotFoundError,
    MenuRepository,
)


def test_get_all_menus_successful_load(tmp_path) -> None:
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

    result = repository.get_all()

    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)

    assert result == _menus

def test_get_all_menus_missing_file(tmp_path) -> None:
    test_file = tmp_path / "missing_menu.json"

    repository = MenuRepository(test_file)

    with raises(MenuDataNotFoundError):
        repository.get_all()

def test_get_all_menus_malformed_data(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"

    test_file.write_text(
        '{"id": "menu_001", "name": "Malformed Burger",',
        encoding="utf-8",
    )

    repository = MenuRepository(test_file)

    with raises(MenuDataMalformedError):
        repository.get_all()

def test_get_all_menus_list_error(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"

    test_file.write_text(
        '{"id": "menu_001", "name": "Not A List"}',
        encoding="utf-8",
    )

    repository = MenuRepository(test_file)

    with raises(MenuDataError):
        repository.get_all()

def test_add_menu_to_empty_file(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"
    test_file.write_text("[]", encoding="utf-8")

    repository = MenuRepository(test_file)

    item = MenuItem(
        id="menu_001",
        restaurant_id="rest_001",
        name="Pho",
        category="Noodles",
        price=14.99,
        is_available=True,
    )

    repository.add(item)

    saved = json.loads(test_file.read_text(encoding="utf-8"))

    assert saved == [item.model_dump()]

def test_add_menu_keeps_existing_items(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"

    _menus = [
        {
            "id": "menu_001",
            "restaurant_id": "rest_001",
            "name": "Cheese Burger",
            "category": "Mains",
            "price": 15.99,
            "is_available": True
        }
    ]

    test_file.write_text(
        json.dumps(_menus),
        encoding="utf-8",
    )

    repository = MenuRepository(test_file)

    item = MenuItem(
        id="menu_002",
        restaurant_id="rest_001",
        name="Pho",
        category="Noodles",
        price=14.99,
        is_available=True,
    )

    repository.add(item)

    saved = repository.get_all()

    assert len(saved) == 2
    assert saved[0] == _menus[0]
    assert saved[1] == item.model_dump()

def test_add_menu_missing_file(tmp_path) -> None:
    test_file = tmp_path / "missing_menu.json"

    repository = MenuRepository(test_file)

    item = MenuItem(
        id="menu_001",
        restaurant_id="rest_001",
        name="Pho",
        category="Noodles",
        price=14.99,
        is_available=True,
    )

    with raises(MenuDataNotFoundError):
        repository.add(item)

def test_update_menu_replaces_matching_item(tmp_path) -> None:
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

    updated = MenuItem(
        id="menu_002",
        restaurant_id="rest_001",
        name="French Fries",
        category="Sides",
        price=3.99,
        is_available=False,
    )

    repository.update(updated)

    saved = repository.get_all()

    assert len(saved) == 2
    assert saved[0] == _menus[0]
    assert saved[1] == updated.model_dump()

def test_update_menu_no_matching_id_changes_nothing(tmp_path) -> None:
    test_file = tmp_path / "menu_items.json"

    _menus = [
        {
            "id": "menu_001",
            "restaurant_id": "rest_001",
            "name": "Cheese Burger",
            "category": "Mains",
            "price": 15.99,
            "is_available": True
        }
    ]

    test_file.write_text(
        json.dumps(_menus),
        encoding="utf-8",
    )

    repository = MenuRepository(test_file)

    item = MenuItem(
        id="menu_999",
        restaurant_id="rest_001",
        name="Ghost Item",
        category="Mains",
        price=9.99,
        is_available=True,
    )

    repository.update(item)

    assert repository.get_all() == _menus

def test_update_menu_missing_file(tmp_path) -> None:
    test_file = tmp_path / "missing_menu.json"

    repository = MenuRepository(test_file)

    item = MenuItem(
        id="menu_001",
        restaurant_id="rest_001",
        name="Pho",
        category="Noodles",
        price=14.99,
        is_available=True,
    )

    with raises(MenuDataNotFoundError):
        repository.update(item)
