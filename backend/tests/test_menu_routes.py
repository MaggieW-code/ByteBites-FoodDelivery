import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def _stored(body: dict) -> dict:
    """How an item is stored inside a restaurant's 'items' list."""
    return {key: value for key, value in body.items() if key != "restaurant_id"}


def test_add_menu_returns_201(client: TestClient, menus_file: Path) -> None:
    response = client.post(
        "/restaurants/rest_001/menu",
        json={
            "name": "Pho",
            "category": "Noodles",
            "price": 14.99,
            "is_available": True,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert len(body["id"]) == 8
    assert body["restaurant_id"] == "rest_001"
    assert body["name"] == "Pho"
    assert body["category"] == "Noodles"
    assert body["price"] == 14.99
    assert body["is_available"] is True

    saved = json.loads(menus_file.read_text(encoding="utf-8"))

    assert len(saved) == 1
    assert saved[0]["restaurant_id"] == "rest_001"
    assert saved[0]["items"] == [_stored(body)]


def test_add_menu_missing_field_returns_422(client: TestClient, menus_file: Path) -> None:
    response = client.post(
        "/restaurants/rest_001/menu",
        json={"name": "Pho"},
    )

    assert response.status_code == 422
    assert json.loads(menus_file.read_text(encoding="utf-8")) == []


def test_add_menu_invalid_price_returns_422(client: TestClient, menus_file: Path) -> None:
    response = client.post(
        "/restaurants/rest_001/menu",
        json={
            "name": "Pho",
            "category": "Noodles",
            "price": 0,
            "is_available": True,
        },
    )

    assert response.status_code == 422
    assert json.loads(menus_file.read_text(encoding="utf-8")) == []


def test_add_menu_user_cannot_set_id(client: TestClient) -> None:
    response = client.post(
        "/restaurants/rest_001/menu",
        json={
            "id": "hacked01",
            "name": "Pho",
            "category": "Noodles",
            "price": 14.99,
            "is_available": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] != "hacked01"


UPDATE_MENUS = [
    {
        "restaurant_id": "rest_001",
        "currency": "CAD",
        "items": [
            {
                "id": "menu_002",
                "name": "French Fries",
                "category": "Sides",
                "description": "",
                "price": 4.99,
                "is_available": True,
            }
        ],
    }
]


@pytest.mark.parametrize("menu_records", [UPDATE_MENUS])
def test_update_menu_returns_200(client: TestClient, menus_file: Path) -> None:
    response = client.patch(
        "/restaurants/rest_001/menu/menu_002",
        json={"price": 3.99},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == "menu_002"
    assert body["restaurant_id"] == "rest_001"
    assert body["price"] == 3.99
    assert body["name"] == "French Fries"

    saved = json.loads(menus_file.read_text(encoding="utf-8"))

    assert saved[0]["items"] == [_stored(body)]


@pytest.mark.parametrize("menu_records", [UPDATE_MENUS])
def test_update_menu_unknown_item_returns_404(client: TestClient, menus_file: Path) -> None:
    response = client.patch(
        "/restaurants/rest_001/menu/menu_999",
        json={"price": 3.99},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Menu item not found"}
    assert json.loads(menus_file.read_text(encoding="utf-8")) == UPDATE_MENUS


@pytest.mark.parametrize("menu_records", [UPDATE_MENUS])
def test_update_menu_wrong_restaurant_returns_404(client: TestClient, menus_file: Path) -> None:
    response = client.patch(
        "/restaurants/rest_002/menu/menu_002",
        json={"price": 3.99},
    )

    assert response.status_code == 404
    assert json.loads(menus_file.read_text(encoding="utf-8")) == UPDATE_MENUS


@pytest.mark.parametrize("menu_records", [UPDATE_MENUS])
def test_update_menu_invalid_price_returns_422(client: TestClient, menus_file: Path) -> None:
    response = client.patch(
        "/restaurants/rest_001/menu/menu_002",
        json={"price": -1},
    )

    assert response.status_code == 422
    assert json.loads(menus_file.read_text(encoding="utf-8")) == UPDATE_MENUS
