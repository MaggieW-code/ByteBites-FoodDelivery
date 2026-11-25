import pytest

from backend.app.models.restaurant_model import Restaurant


@pytest.fixture
def restaurant_records():
    return [
        dict(id="rest_001", name="Sushi", cuisine="Japanese", rating=4.5,
             address="123 Main St", is_active=True),
        dict(id="rest_002", name="Pizza", cuisine="Italian", rating=4.0,
             address="456 Main St", is_active=True),
        dict(id="rest_003", name="Ramen", cuisine="Japanese", rating=4.2,
             address="789 Main St", is_active=True),
    ]


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
def test_service_filters_cuisine(restaurant_service, cuisine, expected_ids):
    result = restaurant_service.get_restaurants(cuisine)
    assert [restaurant.id for restaurant in result] == expected_ids
    assert all(isinstance(restaurant, Restaurant) for restaurant in result)


@pytest.mark.parametrize("cuisine, expected_ids", [
    (None, ["rest_001", "rest_002", "rest_003"]),
    ("  JAPANESE  ", ["rest_001", "rest_003"]),
    ("Unknown", []),
])
def test_api_cuisine_filter(client, cuisine, expected_ids):
    response = client.get("/restaurants", params={} if cuisine is None else {"cuisine": cuisine})
    assert response.status_code == 200
    assert [record["id"] for record in response.json()] == expected_ids
    for record in response.json():
        Restaurant.model_validate(record)
