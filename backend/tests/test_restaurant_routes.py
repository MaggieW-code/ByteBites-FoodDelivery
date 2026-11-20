import pytest
from fastapi.testclient import TestClient

from main import app


def test_get_restaurants_returns_200(client: TestClient) -> None:
    response = client.get("/restaurants")

    assert response.status_code == 200


def test_get_restaurants_returns_list(client: TestClient) -> None:
    response = client.get("/restaurants")

    assert isinstance(response.json(), list)


@pytest.mark.parametrize("restaurant_records", [[]])
def test_get_restaurants_empty_data(client: TestClient) -> None:
    response = client.get("/restaurants")

    assert response.status_code == 200
    assert response.json() == []


INVALID_RATING = {
    "id": "rest_001",
    "name": "Test Restaurant",
    "cuisine": "Chinese",
    "rating": 6.0,
    "address": "123 Test Street",
    "is_active": True,
}


@pytest.mark.usefixtures("client")
@pytest.mark.parametrize("restaurant_records", [[INVALID_RATING]])
def test_get_restaurants_invalid_rating_returns_500() -> None:
    # Separate client that returns the 500 instead of raising it
    with TestClient(app, raise_server_exceptions=False) as test_client:
        response = test_client.get("/restaurants")

    assert response.status_code == 500
