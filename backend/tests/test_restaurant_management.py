import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.repositories.restaurant_repository import RestaurantRepository

ORIGINAL = {
    "id": "rest_001",
    "name": "Burger Craft",
    "cuisine": "American",
    "rating": 4.5,
    "address": "123 Main Street",
    "is_active": True,
}


# Most tests here start with no restaurants
@pytest.fixture
def restaurant_records() -> list[dict]:
    return []


def test_create_restaurant(client: TestClient, restaurants_file: Path) -> None:
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
    saved = json.loads(restaurants_file.read_text(encoding="utf-8"))

    assert len(saved) == 1
    assert saved[0]["id"] == restaurant["id"]


@pytest.mark.parametrize("restaurant_records", [[ORIGINAL]])
def test_update_restaurant(client: TestClient, restaurants_file: Path) -> None:
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
    saved = json.loads(restaurants_file.read_text(encoding="utf-8"))

    assert saved[0]["id"] == "rest_001"
    assert saved[0]["address"] == "456 Bernard Avenue"


def test_update_unknown_restaurant(client: TestClient) -> None:
    response = client.patch(
        "/restaurants/unknown1",
        json={"name": "New Name"},
    )

    assert response.status_code == 404


def test_create_invalid_restaurant(client: TestClient, restaurants_file: Path) -> None:
    response = client.post(
        "/restaurants",
        json={
            "name": "",
            "cuisine": "Italian",
            "address": "123 Main Street",
        },
    )

    assert response.status_code == 422
    assert json.loads(restaurants_file.read_text()) == []


@pytest.mark.parametrize("restaurant_records", [[ORIGINAL]])
def test_update_invalid_restaurant(client: TestClient, restaurants_file: Path) -> None:
    response = client.patch(
        "/restaurants/rest_001",
        json={"name": ""},
    )

    assert response.status_code == 422

    # Invalid updates must not change stored data
    saved = json.loads(restaurants_file.read_text())
    assert saved == [ORIGINAL]


def test_create_unique_ids(client: TestClient) -> None:
    data = {
        "name": "Pizza Palace",
        "cuisine": "Italian",
        "address": "123 Main Street",
    }

    first = client.post("/restaurants", json=data)
    second = client.post("/restaurants", json=data)

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]


def test_restaurant_persistence(client: TestClient, restaurants_file: Path) -> None:
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
    new_repository = RestaurantRepository(restaurants_file)
    restaurants = new_repository.get_all()

    assert len(restaurants) == 1
    assert restaurants[0]["id"] == restaurant_id
    assert restaurants[0]["address"] == "456 Bernard Avenue"
