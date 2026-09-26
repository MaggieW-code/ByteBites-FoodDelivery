import json
from pathlib import Path

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from backend.app.routes import restaurant_routes
from main import app

client = TestClient(app)


def test_get_restaurants_returns_200() -> None:
    response = client.get("/restaurants")

    assert response.status_code == 200

def test_get_restaurants_returns_list():
    response = client.get("/restaurants")

    assert isinstance(response.json(), list)


def test_get_restaurants_empty_data(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    data_path = tmp_path / "restaurants.json"
    data_path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(restaurant_routes.restaurant_repository, "data_path", data_path)

    with TestClient(app) as test_client:
        response = test_client.get("/restaurants")

    assert response.status_code == 200
    assert response.json() == []


def test_get_restaurants_invalid_rating_returns_500(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    data_path = tmp_path / "restaurants.json"
    data_path.write_text(
        json.dumps([
            {
                "id": "rest_001",
                "name": "Test Restaurant",
                "cuisine": "Chinese",
                "rating": 6.0,
                "address": "123 Test Street",
                "is_active": True,
            }
        ]),
        encoding="utf-8",
    )
    monkeypatch.setattr(restaurant_routes.restaurant_repository, "data_path", data_path)

    with TestClient(app, raise_server_exceptions=False) as test_client:
        response = test_client.get("/restaurants")

    assert response.status_code == 500
