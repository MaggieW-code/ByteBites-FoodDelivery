import pytest

from backend.app.models.restaurant_model import Restaurant
from backend.app.services.restaurant_service import RestaurantNotFoundError, RestaurantService


@pytest.fixture
def restaurant_records():
    return [
        dict(id="rest_001", name="First", cuisine="Japanese", rating=4.5,
             address="123 Main St", is_active=True),
        dict(id="rest_002", name="Second", cuisine="Italian", rating=4.0,
             address="456 Main St", is_active=False),
    ]


def test_repository_lookup(restaurant_repository):
    assert restaurant_repository.get_by_id("rest_002")["name"] == "Second"
    assert restaurant_repository.get_by_id("rest_999") is None


def test_service_lookup(restaurant_repository):
    result = RestaurantService(restaurant_repository).get_restaurant_by_id("rest_002")
    assert isinstance(result, Restaurant)
    assert result.id == "rest_002"
    assert result.is_active is False


def test_service_unknown_id(restaurant_repository):
    with pytest.raises(RestaurantNotFoundError):
        RestaurantService(restaurant_repository).get_restaurant_by_id("rest_999")


def test_details_response(client, restaurant_repository):
    response = client.get("/restaurants/rest_002")
    assert response.status_code == 200
    assert response.json() == restaurant_repository.get_by_id("rest_002")
    Restaurant.model_validate(response.json())


def test_unknown_id_returns_404(client):
    response = client.get("/restaurants/rest_999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Restaurant 'rest_999' not found"}


@pytest.mark.parametrize("identifier", ["short", "rest_0001"])
def test_invalid_id_returns_422(client, identifier):
    assert client.get(f"/restaurants/{identifier}").status_code == 422
