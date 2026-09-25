import json

from pytest import raises

from backend.app.repositories.restaurant_repository import (
    RestaurantDataError,
    RestaurantDataMalformedError,
    RestaurantDataNotFoundError,
    RestaurantRepository,
)


def test_get_all_restaurants_successful_load(tmp_path) -> None:
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

    result = repository.get_all()

    assert isinstance(result, list)
    assert all(isinstance(item, dict) for item in result)

    assert result == _restaurants

def test_get_all_restaurants_missing_file(tmp_path) -> None:
    test_file = tmp_path / "missing_restaurant.json"
    
    repository = RestaurantRepository(test_file)

    with raises(RestaurantDataNotFoundError): 
        repository.get_all()

def test_get_all_restaurants_malformed_data(tmp_path) -> None:
    test_file = tmp_path / "missing_restaurant.json"

    test_file.write_text(
        '{"id": "rest_002", "name": "Malformed Burgers",',
        encoding="utf-8",
    )
    
    repository = RestaurantRepository(test_file)

    with raises(RestaurantDataMalformedError): 
        repository.get_all()

def test_get_all_restaurants_list_error(tmp_path) -> None:
    test_file = tmp_path / "missing_restaurant.json"

    test_file.write_text(
        '{"id": "rest_002", "name": "Malformed Burgers"}',
        encoding="utf-8",
    )

    repository = RestaurantRepository(test_file)

    with raises(RestaurantDataError): 
        repository.get_all()
