from pydantic import ValidationError
from pytest import raises

from backend.app.models.menu_Item_model import CreateMenuItem, MenuItem


def test_create_menu_item_model_successful() -> None:
    item = CreateMenuItem(
        name="Pho",
        category="Noodles",
        price=14.99,
        is_available=True,
    )

    assert item.name == "Pho"
    assert item.category == "Noodles"
    assert item.price == 14.99
    assert item.is_available is True

def test_menu_item_model_successful() -> None:
    item = MenuItem(
        id="menu_001",
        restaurant_id="rest_001",
        name="Pho",
        category="Noodles",
        price=14.99,
        is_available=True,
    )

    assert item.id == "menu_001"
    assert item.restaurant_id == "rest_001"
    assert item.name == "Pho"
    assert item.category == "Noodles"
    assert item.price == 14.99
    assert item.is_available is True

def test_menu_item_model_missing_id() -> None:
    with raises(ValidationError):
        MenuItem(
            restaurant_id="rest_001",
            name="Pho",
            category="Noodles",
            price=14.99,
            is_available=True,
        )

def test_menu_item_model_invalid_id_length_min() -> None:
    with raises(ValidationError):
        MenuItem(
            id="menu_01",
            restaurant_id="rest_001",
            name="Pho",
            category="Noodles",
            price=14.99,
            is_available=True,
        )

def test_menu_item_model_invalid_id_length_max() -> None:
    with raises(ValidationError):
        MenuItem(
            id="menu_0001",
            restaurant_id="rest_001",
            name="Pho",
            category="Noodles",
            price=14.99,
            is_available=True,
        )

def test_menu_item_model_invalid_restaurant_id_length() -> None:
    with raises(ValidationError):
        MenuItem(
            id="menu_001",
            restaurant_id="rest_1",
            name="Pho",
            category="Noodles",
            price=14.99,
            is_available=True,
        )

def test_menu_item_model_empty_name() -> None:
    with raises(ValidationError):
        MenuItem(
            id="menu_001",
            restaurant_id="rest_001",
            name="",
            category="Noodles",
            price=14.99,
            is_available=True,
        )

def test_menu_item_model_empty_category() -> None:
    with raises(ValidationError):
        MenuItem(
            id="menu_001",
            restaurant_id="rest_001",
            name="Pho",
            category="",
            price=14.99,
            is_available=True,
        )

def test_menu_item_model_zero_price() -> None:
    with raises(ValidationError):
        MenuItem(
            id="menu_001",
            restaurant_id="rest_001",
            name="Pho",
            category="Noodles",
            price=0,
            is_available=True,
        )

def test_menu_item_model_negative_price() -> None:
    with raises(ValidationError):
        MenuItem(
            id="menu_001",
            restaurant_id="rest_001",
            name="Pho",
            category="Noodles",
            price=-5.0,
            is_available=True,
        )

def test_menu_item_model_price_as_string() -> None:
    with raises(ValidationError):
        MenuItem(
            id="menu_001",
            restaurant_id="rest_001",
            name="Pho",
            category="Noodles",
            price="14.99",
            is_available=True,
        )

def test_menu_item_model_is_available_as_string() -> None:
    with raises(ValidationError):
        MenuItem(
            id="menu_001",
            restaurant_id="rest_001",
            name="Pho",
            category="Noodles",
            price=14.99,
            is_available="True",
        )
