from pydantic import ValidationError
from pytest import raises

from backend.app.models.update_menu_item_model import UpdateMenuItem


def test_update_menu_item_model_all_fields() -> None:
    item = UpdateMenuItem(
        name="Pho",
        category="Noodles",
        price=14.99,
        is_available=False,
    )

    assert item.name == "Pho"
    assert item.category == "Noodles"
    assert item.price == 14.99
    assert item.is_available is False

def test_update_menu_item_model_only_price() -> None:
    item = UpdateMenuItem(price=3.99)

    assert item.price == 3.99
    assert item.name is None
    assert item.category is None
    assert item.is_available is None

def test_update_menu_item_model_no_fields() -> None:
    item = UpdateMenuItem()

    assert item.model_dump(exclude_none=True) == {}

def test_update_menu_item_model_empty_name() -> None:
    with raises(ValidationError):
        UpdateMenuItem(name="")

def test_update_menu_item_model_empty_category() -> None:
    with raises(ValidationError):
        UpdateMenuItem(category="")

def test_update_menu_item_model_zero_price() -> None:
    with raises(ValidationError):
        UpdateMenuItem(price=0)

def test_update_menu_item_model_negative_price() -> None:
    with raises(ValidationError):
        UpdateMenuItem(price=-5.0)

def test_update_menu_item_model_price_as_string() -> None:
    with raises(ValidationError):
        UpdateMenuItem(price="3.99")

def test_update_menu_item_model_is_available_as_string() -> None:
    with raises(ValidationError):
        UpdateMenuItem(is_available="False")
