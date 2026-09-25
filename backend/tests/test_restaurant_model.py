from pytest import raises
from pydantic import ValidationError

from backend.app.models.restaurant_model import Restaurant


def test_restaurant_model_successful() -> None:
    restaurant = Restaurant(
        id="rest_000",
        name="Wasabi",
        cuisine="Japanese",
        rating=4.5,
        address="123 Main St",
        active=True,
    )

    assert restaurant.id == "rest_000"
    assert restaurant.name == "Wasabi"
    assert restaurant.cuisine == "Japanese"
    assert restaurant.rating == 4.5
    assert restaurant.address == "123 Main St"
    assert restaurant.active is True

def test_restaurant_model_invalid_id_length_min() -> None:
    with raises(ValidationError):
        Restaurant(
            id="rest_01",
            name="Wasabi",
            cuisine="Japanese",
            rating=4.5,
            address="123 Main St",
            active=True,
        )

def test_restaurant_model_invalid_id_length_max() -> None:
    with raises(ValidationError):
        Restaurant(
            id="rest_0001",
            name="Wasabi",
            cuisine="Japanese",
            rating=4.5,
            address="123 Main St",
            active=True,
        )

def test_restaurant_model_invalid_name_length() -> None:
    with raises(ValidationError):
        Restaurant(
            id="rest_001",
            name="",
            cuisine="Japanese",
            rating=4.5,
            address="123 Main St",
            active=True,
        )

def test_restaurant_model_invalid_cuisine_length() -> None:
    with raises(ValidationError):
        Restaurant(
            id="rest_001",
            name="Wasabi",
            cuisine="",
            rating=4.5,
            address="123 Main St",
            active=True,
        )

def test_restaurant_model_invalid_rating_scope() -> None:
    with raises(ValidationError):
        Restaurant(
            id="rest_001",
            name="Wasabi",
            cuisine="Japanese",
            rating=6.0,
            address="123 Main St",
            active=True,
        )

def test_restaurant_model_invalid_rating_strict() -> None:
    with raises(ValidationError):
        Restaurant(
            id="rest_001",
            name="Wasabi",
            cuisine="Japanese",
            rating="4.5",
            address="123 Main St",
            active=True,
        )

def test_restaurant_model_invalid_address_length() -> None:
    with raises(ValidationError):
        Restaurant(
            id="rest_01",
            name="Wasabi",
            cuisine="Japanese",
            rating=4.5,
            address="",
            active=True,
        )

def test_restaurant_model_invalid_active_strict() -> None:
    with raises(ValidationError):
        Restaurant(
            id="rest_001",
            name="Wasabi",
            cuisine="Japanese",
            rating=4.5,
            address="123 Main St",
            active="True",
        )
