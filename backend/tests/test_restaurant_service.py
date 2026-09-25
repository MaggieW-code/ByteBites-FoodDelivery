import json

from pydantic import ValidationError
from pytest import raises

from backend.app.models.restaurant_model import Restaurant
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services.restaurant_service import RestaurantService


def test_validate_get_restaurants_service(tmp_path) -> None:
    test_file = tmp_path / "restaurants.json"

    _restaurants = [
        {
            "id": "rest_001",
            "name": "Burger King",
            "cuisine": "American",
            "rating": 4.5,
            "address": "521 Main Street, Kelowna, BC",
            "is_active": True
        },
        {
            "id": "rest_002",
            "name": "McDonalds",
            "cuisine": "Fast Food",
            "rating": 4.7,
            "address": "123 West Street, Kelowna, BC",
            "is_active": True   
        }

    ]

    test_file.write_text(
        json.dumps(_restaurants),
        encoding="utf-8",
    )

    repository = RestaurantRepository(test_file)
    service = RestaurantService(repository)

    data = service.get_restaurants()

    assert isinstance(data, list)
    assert all(isinstance(item, Restaurant) for item in data)

    assert data[0].id == "rest_001"
    assert data[0].name == "Burger King"
    assert data[1].id == "rest_002"
    assert data[1].name == "McDonalds"

def test_validate_get_restaurants_service_id_fail(tmp_path) -> None:
    test_file = tmp_path / "restaurants.json"

    _restaurants = [
        {
            "id": "rest_01",
            "name": "Burger King",
            "cuisine": "American",
            "rating": 4.5,
            "address": "521 Main Street, Kelowna, BC",
            "is_active": True
        },
        {
            "id": "rest_002",
            "name": "McDonalds",
            "cuisine": "Fast Food",
            "rating": 4.7,
            "address": "123 West Street, Kelowna, BC",
            "is_active": True   
        }

    ]

    test_file.write_text(
        json.dumps(_restaurants),
        encoding="utf-8",
    )

    repository = RestaurantRepository(test_file)
    service = RestaurantService(repository)

    with raises(ValidationError):
        service.get_restaurants()

def test_validate_get_restaurants_service_name_fail(tmp_path) -> None:
    test_file = tmp_path / "restaurants.json"

    _restaurants = [
        {
            "id": "rest_001",
            "name": "",
            "cuisine": "American",
            "rating": 4.5,
            "address": "521 Main Street, Kelowna, BC",
            "is_active": True
        },
        {
            "id": "rest_002",
            "name": "McDonalds",
            "cuisine": "Fast Food",
            "rating": 4.7,
            "address": "123 West Street, Kelowna, BC",
            "is_active": True   
        }

    ]

    test_file.write_text(
        json.dumps(_restaurants),
        encoding="utf-8",
    )

    repository = RestaurantRepository(test_file)
    service = RestaurantService(repository)

    with raises(ValidationError):
        service.get_restaurants()

def test_validate_get_restaurants_service_cuisine_fail(tmp_path) -> None:
    test_file = tmp_path / "restaurants.json"

    _restaurants = [
        {
            "id": "rest_001",
            "name": "Burger King",
            "cuisine": "",
            "rating": 4.5,
            "address": "521 Main Street, Kelowna, BC",
            "is_active": True
        },
        {
            "id": "rest_002",
            "name": "McDonalds",
            "cuisine": "Fast Food",
            "rating": 4.7,
            "address": "123 West Street, Kelowna, BC",
            "is_active": True   
        }

    ]

    test_file.write_text(
        json.dumps(_restaurants),
        encoding="utf-8",
    )

    repository = RestaurantRepository(test_file)
    service = RestaurantService(repository)

    with raises(ValidationError):
        service.get_restaurants()

def test_validate_get_restaurants_service_rating_fail(tmp_path) -> None:
    test_file = tmp_path / "restaurants.json"

    _restaurants = [
        {
            "id": "rest_001",
            "name": "Burger King",
            "cuisine": "American",
            "rating": 6.0,
            "address": "521 Main Street, Kelowna, BC",
            "is_active": True
        },
        {
            "id": "rest_002",
            "name": "McDonalds",
            "cuisine": "Fast Food",
            "rating": 4.7,
            "address": "123 West Street, Kelowna, BC",
            "is_active": True   
        }

    ]

    test_file.write_text(
        json.dumps(_restaurants),
        encoding="utf-8",
    )

    repository = RestaurantRepository(test_file)
    service = RestaurantService(repository)

    with raises(ValidationError):
        service.get_restaurants()

def test_validate_get_restaurants_service_address_fail(tmp_path) -> None:
    test_file = tmp_path / "restaurants.json"

    _restaurants = [
        {
            "id": "rest_001",
            "name": "Burger King",
            "cuisine": "American",
            "rating": 4.5,
            "address": "",
            "is_active": True
        },
        {
            "id": "rest_002",
            "name": "McDonalds",
            "cuisine": "Fast Food",
            "rating": 4.7,
            "address": "123 West Street, Kelowna, BC",
            "is_active": True   
        }

    ]

    test_file.write_text(
        json.dumps(_restaurants),
        encoding="utf-8",
    )

    repository = RestaurantRepository(test_file)
    service = RestaurantService(repository)

    with raises(ValidationError):
        service.get_restaurants()

def test_validate_get_restaurants_service_is_active_fail(tmp_path) -> None:
    test_file = tmp_path / "restaurants.json"

    _restaurants = [
        {
            "id": "rest_001",
            "name": "Burger King",
            "cuisine": "American",
            "rating": 4.5,
            "address": "521 Main Street, Kelowna, BC",
            "is_active": "True"
        },
        {
            "id": "rest_002",
            "name": "McDonalds",
            "cuisine": "Fast Food",
            "rating": 4.7,
            "address": "123 West Street, Kelowna, BC",
            "is_active": True   
        }

    ]

    test_file.write_text(
        json.dumps(_restaurants),
        encoding="utf-8",
    )

    repository = RestaurantRepository(test_file)
    service = RestaurantService(repository)

    with raises(ValidationError):
        service.get_restaurants()