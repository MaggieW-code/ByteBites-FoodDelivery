import json

import pytest
from fastapi.testclient import TestClient

from backend.app.models.restaurant_model import Restaurant
from backend.app.repositories.restaurant_repository import (
    RestaurantRepository, RestaurantDataNotFoundError, RestaurantDataMalformedError,
)
from backend.app.routes import restaurant_routes
from backend.app.services.restaurant_service import RestaurantService, RestaurantNotFoundError
from main import app


@pytest.fixture
def repository(tmp_path):
    records = [
        dict(id="rest_001", name="First", cuisine="Japanese", rating=4.5,
             address="123 Main St", is_active=True),
        dict(id="rest_002", name="Second", cuisine="Italian", rating=4.0,
             address="456 Main St", is_active=False),
    ]
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(records), encoding="utf-8")
    return RestaurantRepository(path)


def test_repository_lookup(repository):
    assert repository.get_by_id("rest_002")["name"] == "Second"
    assert repository.get_by_id("rest_999") is None


def test_service_lookup(repository):
    result = RestaurantService(repository).get_restaurant_by_id("rest_002")
    assert isinstance(result, Restaurant)
    assert result.id == "rest_002"
    assert result.is_active is False


def test_service_unknown_id(repository):
    with pytest.raises(RestaurantNotFoundError):
        RestaurantService(repository).get_restaurant_by_id("rest_999")


@pytest.fixture
def client(repository, monkeypatch):
    monkeypatch.setattr(restaurant_routes, "restaurant_service", RestaurantService(repository))
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


def test_details_response(client, repository):
    response = client.get("/restaurants/rest_002")
    assert response.status_code == 200
    assert response.json() == repository.get_by_id("rest_002")
    Restaurant.model_validate(response.json())


def test_unknown_id_returns_404(client):
    response = client.get("/restaurants/rest_999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Restaurant 'rest_999' not found"}


@pytest.mark.parametrize("identifier", ["short", "rest_0001"])
def test_invalid_id_returns_422(client, identifier):
    assert client.get(f"/restaurants/{identifier}").status_code == 422
