import json

import pytest
from fastapi.testclient import TestClient

from backend.app.models.restaurant_model import Restaurant
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.routes import restaurant_routes
from backend.app.services.restaurant_service import RestaurantService
from main import app


@pytest.fixture
def service(tmp_path):
    records = [
        dict(id="rest_001", name="Sushi", cuisine="Japanese", rating=4.5,
             address="123 Main St", is_active=True),
        dict(id="rest_002", name="Pizza", cuisine="Italian", rating=4.0,
             address="456 Main St", is_active=True),
        dict(id="rest_003", name="Ramen", cuisine="Japanese", rating=4.2,
             address="789 Main St", is_active=True),
    ]
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(records), encoding="utf-8")
    return RestaurantService(RestaurantRepository(path))


@pytest.mark.parametrize("cuisine, expected_ids", [
    (None, ["rest_001", "rest_002", "rest_003"]),
    ("", ["rest_001", "rest_002", "rest_003"]),
    ("   ", ["rest_001", "rest_002", "rest_003"]),
    ("Japanese", ["rest_001", "rest_003"]),
    ("  jApAnEsE  ", ["rest_001", "rest_003"]),
    ("Italian", ["rest_002"]),
    ("Unknown", []),
    ("Japan", []),
])
def test_service_filters_cuisine(service, cuisine, expected_ids):
    result = service.get_restaurants(cuisine)
    assert [restaurant.id for restaurant in result] == expected_ids
    assert all(isinstance(restaurant, Restaurant) for restaurant in result)


@pytest.mark.parametrize("cuisine, expected_ids", [
    (None, ["rest_001", "rest_002", "rest_003"]),
    ("  JAPANESE  ", ["rest_001", "rest_003"]),
    ("Unknown", []),
])
def test_api_cuisine_filter(service, monkeypatch, cuisine, expected_ids):
    monkeypatch.setattr(restaurant_routes, "restaurant_service", service)
    with TestClient(app) as client:
        response = client.get("/restaurants", params={} if cuisine is None else {"cuisine": cuisine})
    assert response.status_code == 200
    assert [record["id"] for record in response.json()] == expected_ids
    for record in response.json():
        Restaurant.model_validate(record)
