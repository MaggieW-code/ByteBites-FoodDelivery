import json
from decimal import Decimal

from pytest import raises

from backend.app.models.menu_model import CreateMenuItem, Menu, MenuItem, UpdateMenuItem
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services import menu_service as menu_service_module
from backend.app.services.menu_service import (
    MenuItemNotFoundError,
    MenuRestaurantInactiveError,
    MenuRestaurantNotFoundError,
    MenuService,
)


def _entry(item: MenuItem) -> dict:
    return item.model_dump(mode="json",exclude={"restaurant_id"})


def _make_service(tmp_path, menus: list[dict]) -> tuple[MenuService, MenuRepository, list[dict]]:
    menu_file = tmp_path / "menus.json"
    menu_file.write_text(json.dumps(menus), encoding="utf-8")

    restaurant_file = tmp_path / "restaurants.json"
    restaurant_file.write_text(
        json.dumps(
            [
                {
                    "id": "rest_001",
                    "name": "Burger Place",
                    "cuisine": "American",
                    "address": "1 Main St",
                    "rating": 4.5,
                    "is_active": True,
                },
                {
                    "id": "rest_002",
                    "name": "Sushi Place",
                    "cuisine": "Japanese",
                    "address": "2 Main St",
                    "rating": 4.0,
                    "is_active": True,
                },
            ]
        ),
        encoding="utf-8",
    )

    menu_repository = MenuRepository(menu_file)
    service = MenuService(menu_repository, RestaurantRepository(restaurant_file))
    return service, menu_repository, menus


def _two_item_menus() -> list[dict]:
    return [
        {
            "restaurant_id": "rest_001",
            "currency": "CAD",
            "items": [
                {
                    "id": "menu_001",
                    "name": "Cheese Burger",
                    "category": "Mains",
                    "description": "",
                    "price": "15.99",
                    "is_available": True,
                },
                {
                    "id": "menu_002",
                    "name": "French Fries",
                    "category": "Sides",
                    "description": "",
                    "price": "4.99",
                    "is_available": True,
                },
            ],
        }
    ]


def _new_item_data() -> CreateMenuItem:
    return CreateMenuItem(
        name="Pho",
        category="Noodles",
        price=14.99,
        is_available=True,
    )


def test_add_menu_service(tmp_path) -> None:
    service, repository, _ = _make_service(tmp_path, [])

    item = service.add_menu("rest_001", _new_item_data())

    assert isinstance(item, MenuItem)
    assert len(item.id) == 8
    assert item.restaurant_id == "rest_001"
    assert item.name == "Pho"
    assert item.category == "Noodles"
    assert item.price == Decimal("14.99")
    assert item.is_available is True

    saved = repository.get_all()

    assert len(saved) == 1
    assert saved[0]["restaurant_id"] == "rest_001"
    assert saved[0]["items"] == [_entry(item)]


def test_add_menu_service_creates_different_ids(tmp_path) -> None:
    service, repository, _ = _make_service(tmp_path, [])

    first = service.add_menu("rest_001", _new_item_data())
    second = service.add_menu("rest_001", _new_item_data())

    assert first.id != second.id
    saved = repository.get_all()
    assert len(saved) == 1
    assert len(saved[0]["items"]) == 2


def test_add_menu_service_invalid_restaurant_id(tmp_path) -> None:
    service, repository, _ = _make_service(tmp_path, [])

    with raises(MenuRestaurantNotFoundError):
        service.add_menu("rest_1", _new_item_data())

    assert repository.get_all() == []

def test_add_menu_service_unknown_restaurant(tmp_path) -> None:
    service, repository, _ = _make_service(tmp_path, [])

    with raises(MenuRestaurantNotFoundError):
        service.add_menu("rest_999", _new_item_data())

    assert repository.get_all() == []

def test_get_menu_service(tmp_path) -> None:
    service, _, _ = _make_service(tmp_path, _two_item_menus())

    menu = service.get_menu("rest_001")

    assert isinstance(menu, Menu)
    assert menu.restaurant_id == "rest_001"
    assert menu.currency == "CAD"
    assert menu.items[0].id == "menu_001"
    assert menu.items[0].name == "Cheese Burger"
    assert menu.items[1].id == "menu_002"
    assert menu.items[1].name == "French Fries"


def test_get_menu_service_restaurant_without_menu_is_empty(tmp_path) -> None:
    service, _, _ = _make_service(tmp_path, _two_item_menus())

    menu = service.get_menu("rest_002")

    assert menu.restaurant_id == "rest_002"
    assert menu.items == []


def test_get_menu_item_service_returns_item(tmp_path) -> None:
    service, _, _ = _make_service(tmp_path, _two_item_menus())

    item = service.get_menu_item("menu_002")

    assert isinstance(item, MenuItem)
    assert item.price == Decimal("4.99")
    assert item.is_available is True
    assert item.restaurant_id == "rest_001"


def test_get_menu_item_service_unknown_item(tmp_path) -> None:
    service, _, _ = _make_service(tmp_path, _two_item_menus())

    with raises(MenuItemNotFoundError):
        service.get_menu_item("menu_999")


def test_get_menu_item_service_inactive_restaurant(tmp_path) -> None:
    service, _, _ = _make_service(tmp_path, _two_item_menus())
    restaurant_file = tmp_path / "restaurants.json"
    restaurants = json.loads(restaurant_file.read_text(encoding="utf-8"))
    restaurants[0]["is_active"] = False
    restaurant_file.write_text(json.dumps(restaurants), encoding="utf-8")

    with raises(MenuRestaurantInactiveError):
        service.get_menu_item("menu_002")


def test_get_menu_item_service_missing_restaurant(tmp_path) -> None:
    menus = _two_item_menus()
    menus[0]["restaurant_id"] = "rest_009"
    service, _, _ = _make_service(tmp_path, menus)

    with raises(MenuRestaurantNotFoundError):
        service.get_menu_item("menu_002")


def test_get_menu_service_unknown_restaurant(tmp_path) -> None:
    service, _, _ = _make_service(tmp_path, _two_item_menus())

    with raises(MenuRestaurantNotFoundError):
        service.get_menu("rest_999")


def test_update_menu_service_only_price(tmp_path) -> None:
    service, repository, menus = _make_service(tmp_path, _two_item_menus())

    updated = service.update_menu("rest_001", "menu_002", UpdateMenuItem(price=3.99))

    assert isinstance(updated, MenuItem)
    assert updated.id == "menu_002"
    assert updated.restaurant_id == "rest_001"
    assert updated.price == Decimal("3.99")
    assert updated.name == "French Fries"
    assert updated.category == "Sides"
    assert updated.is_available is True

    saved = repository.get_all()

    assert saved[0]["items"][0] == menus[0]["items"][0]
    assert saved[0]["items"][1] == _entry(updated)


def test_update_menu_service_all_fields(tmp_path) -> None:
    service, _, _ = _make_service(tmp_path, _two_item_menus())

    data = UpdateMenuItem(
        name="Curly Fries",
        category="Snacks",
        price=5.49,
        is_available=False,
    )

    updated = service.update_menu("rest_001", "menu_002", data)

    assert updated.name == "Curly Fries"
    assert updated.category == "Snacks"
    assert updated.price == Decimal("5.49")
    assert updated.is_available is False
    assert updated.id == "menu_002"
    assert updated.restaurant_id == "rest_001"


def test_update_menu_service_no_fields_changes_nothing(tmp_path) -> None:
    service, repository, menus = _make_service(tmp_path, _two_item_menus())

    updated = service.update_menu("rest_001", "menu_002", UpdateMenuItem())

    assert _entry(updated) == menus[0]["items"][1]
    assert repository.get_all() == menus


def test_update_menu_service_unknown_item(tmp_path) -> None:
    service, repository, menus = _make_service(tmp_path, _two_item_menus())

    with raises(MenuItemNotFoundError):
        service.update_menu("rest_001", "menu_999", UpdateMenuItem(price=3.99))

    assert repository.get_all() == menus


def test_update_menu_service_wrong_restaurant(tmp_path) -> None:
    service, repository, menus = _make_service(tmp_path, _two_item_menus())

    with raises(MenuItemNotFoundError):
        service.update_menu("rest_002", "menu_002", UpdateMenuItem(price=3.99))

    assert repository.get_all() == menus


def test_update_menu_service_shows_in_get_menu(tmp_path) -> None:
    service, _, _ = _make_service(tmp_path, _two_item_menus())

    service.update_menu("rest_001", "menu_002", UpdateMenuItem(price=3.99))

    menu = service.get_menu("rest_001")

    assert menu.items[1].id == "menu_002"
    assert float(menu.items[1].price) == 3.99

def test_saved_price_loads_back_as_exact_decimal(tmp_path) -> None:
    service, repository, _ = _make_service(tmp_path, [])

    item = service.add_menu("rest_001", CreateMenuItem(
        name="Pho", category="Noodles", price=14.99, is_available=True))

    loaded = repository.find_item("rest_001", item.id)
    assert Decimal(loaded["price"]) == Decimal("14.99")


def test_add_menu_service_skips_id_already_used_by_another_restaurant(tmp_path, monkeypatch) -> None:
    # "menu_001" already belongs to rest_001; adding to rest_002 must not reuse it
    service, repository, _ = _make_service(tmp_path, _two_item_menus())

    class FakeUuid:
        def __init__(self, hex_value: str):
            self.hex = hex_value

    generated = iter([FakeUuid("menu_001" + "0" * 24), FakeUuid("newid_01" + "0" * 24)])
    monkeypatch.setattr(menu_service_module.uuid, "uuid4", lambda: next(generated))

    item = service.add_menu("rest_002", _new_item_data())

    assert item.id == "newid_01"
    assert service.get_menu_item("menu_001").restaurant_id == "rest_001"
    assert service.get_menu_item("newid_01").restaurant_id == "rest_002"


def test_get_menu_item_service_free_item(tmp_path) -> None:
    # Checkout (#144) relies on free items: a stored price of "0" must load
    menus = _two_item_menus()
    menus[0]["items"][1]["price"] = "0"
    service, _, _ = _make_service(tmp_path, menus)

    item = service.get_menu_item("menu_002")

    assert item.price == Decimal("0")
