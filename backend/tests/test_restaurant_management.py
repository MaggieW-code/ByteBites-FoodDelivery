
import json

from fastapi.testclient import TestClient

from backend.app.routes import restaurant_routes
from main import app


def test_create_restaurant(tmp_path, monkeypatch):
    # Create a temporary JSON file
    test_file = tmp_path / "restaurants.json"
    test_file.write_text("[]", encoding="utf-8")

    # Use the temporary file instead of real data
    monkeypatch.setattr(
        restaurant_routes.restaurant_repository,
        "data_path",
        test_file,
    )

    with TestClient(app) as client:
        response = client.post(
            "/restaurants",
            json={
                "name": "Pizza Palace",
                "cuisine": "Italian",
                "address": "123 Main Street",
            },
        )

        assert response.status_code == 201

        restaurant = response.json()

        assert restaurant["name"] == "Pizza Palace"
        assert len(restaurant["id"]) == 8
        assert restaurant["rating"] == 0.0
        assert restaurant["is_active"] is True

        # Verify data was saved to JSON
        saved = json.loads(
            test_file.read_text(encoding="utf-8")
        )

        assert len(saved) == 1
        assert saved[0]["id"] == restaurant["id"]


def test_update_restaurant(tmp_path, monkeypatch):
    test_file = tmp_path / "restaurants.json"

    original = {
        "id": "rest_001",
        "name": "Burger Craft",
        "cuisine": "American",
        "rating": 4.5,
        "address": "123 Main Street",
        "is_active": True,
    }

    test_file.write_text(
        json.dumps([original]),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        restaurant_routes.restaurant_repository,
        "data_path",
        test_file,
    )

    with TestClient(app) as client:
        response = client.patch(
            "/restaurants/rest_001",
            json={"address": "456 Bernard Avenue"},
        )

        assert response.status_code == 200

        updated = response.json()

        assert updated["id"] == "rest_001"
        assert updated["name"] == "Burger Craft"
        assert updated["cuisine"] == "American"
        assert updated["address"] == "456 Bernard Avenue"

        # Verify the update was saved to JSON
        saved = json.loads(
            test_file.read_text(encoding="utf-8")
        )

        assert saved[0]["id"] == "rest_001"
        assert saved[0]["address"] == "456 Bernard Avenue"


def test_update_unknown_restaurant(tmp_path, monkeypatch):
    test_file = tmp_path / "restaurants.json"
    test_file.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(
        restaurant_routes.restaurant_repository,
        "data_path",
        test_file,
    )

    with TestClient(app) as client:
        response = client.patch(
            "/restaurants/unknown1",
            json={"name": "New Name"},
        )

    assert response.status_code == 404


def test_create_invalid_restaurant(tmp_path, monkeypatch):
    test_file = tmp_path / "restaurants.json"
    test_file.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(
        restaurant_routes.restaurant_repository,
        "data_path",
        test_file,
    )

    with TestClient(app) as client:
        response = client.post(
            "/restaurants",
            json={
                "name": "",
                "cuisine": "Italian",
                "address": "123 Main Street",
            },
        )

    assert response.status_code == 422
    assert json.loads(test_file.read_text()) == []


def test_update_invalid_restaurant(tmp_path, monkeypatch):
    test_file = tmp_path / "restaurants.json"

    original = {
        "id": "rest_001",
        "name": "Burger Craft",
        "cuisine": "American",
        "rating": 4.5,
        "address": "123 Main Street",
        "is_active": True,
    }

    test_file.write_text(
        json.dumps([original]),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        restaurant_routes.restaurant_repository,
        "data_path",
        test_file,
    )

    with TestClient(app) as client:
        response = client.patch(
            "/restaurants/rest_001",
            json={"name": ""},
        )

    assert response.status_code == 422

    # Invalid updates must not change stored data
    saved = json.loads(test_file.read_text())
    assert saved == [original]


def test_create_unique_ids(tmp_path, monkeypatch):
    test_file = tmp_path / "restaurants.json"
    test_file.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(
        restaurant_routes.restaurant_repository,
        "data_path",
        test_file,
    )

    data = {
        "name": "Pizza Palace",
        "cuisine": "Italian",
        "address": "123 Main Street",
    }

    with TestClient(app) as client:
        first = client.post("/restaurants", json=data)
        second = client.post("/restaurants", json=data)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]


def test_restaurant_persistence(tmp_path, monkeypatch):
    from backend.app.repositories.restaurant_repository import (
        RestaurantRepository,
    )

    test_file = tmp_path / "restaurants.json"
    test_file.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(
        restaurant_routes.restaurant_repository,
        "data_path",
        test_file,
    )

    with TestClient(app) as client:
        created = client.post(
            "/restaurants",
            json={
                "name": "Pizza Palace",
                "cuisine": "Italian",
                "address": "123 Main Street",
            },
        )

        assert created.status_code == 201
        restaurant_id = created.json()["id"]

        updated = client.patch(
            f"/restaurants/{restaurant_id}",
            json={"address": "456 Bernard Avenue"},
        )

        assert updated.status_code == 200

    # Simulate loading data in a new repository instance
    new_repository = RestaurantRepository(test_file)
    restaurants = new_repository.get_all()

    assert len(restaurants) == 1
    assert restaurants[0]["id"] == restaurant_id
    assert restaurants[0]["address"] == "456 Bernard Avenue"
