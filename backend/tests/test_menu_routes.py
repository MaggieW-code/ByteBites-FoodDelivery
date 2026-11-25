import json
from decimal import Decimal
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
    assert body["price"] == "14.99"
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
            "price": -1,
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


def test_add_menu_unknown_restaurant_returns_404(client: TestClient, menus_file: Path) -> None:
    response = client.post(
        "/restaurants/rest_999/menu",
        json={
            "name": "Pho",
            "category": "Noodles",
            "price": 14.99,
            "is_available": True,
        },
    )

    assert response.status_code == 404
    assert json.loads(menus_file.read_text(encoding="utf-8")) == []


def test_add_menu_existing_restaurant_returns_201(client: TestClient) -> None:
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
    assert response.json()["restaurant_id"] == "rest_001"


@pytest.mark.parametrize("bad_id", ["rest_01", "rest_0001", "r"])
def test_add_menu_bad_restaurant_id_length_returns_422(client: TestClient, menus_file: Path, bad_id: str) -> None:
    response = client.post(
        f"/restaurants/{bad_id}/menu",
        json={
            "name": "Pho",
            "category": "Noodles",
            "price": 14.99,
            "is_available": True,
        },
    )

    assert response.status_code == 422
    assert json.loads(menus_file.read_text(encoding="utf-8")) == []


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
    assert body["price"] == "3.99"
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


# --- price format (PR #132 review) ---
# Accepted: JSON number or decimal string, >= 0 (0 = free item), at most 2 decimal places, at most 999999.99.


@pytest.mark.parametrize("price", [14.99, "14.99"])
def test_add_menu_accepts_number_or_decimal_string_price(client: TestClient, menus_file: Path, price) -> None:
    response = client.post(
        "/restaurants/rest_001/menu",
        json={"name": "Pho", "category": "Noodles", "price": price, "is_available": True},
    )
    assert response.status_code == 201
    assert response.json()["price"] == "14.99"

    # saved and reloaded exactly
    saved = json.loads(menus_file.read_text(encoding="utf-8"))
    assert saved[0]["items"][0]["price"] == "14.99"
    menu = client.get("/restaurants/rest_001/menu").json()
    assert menu["items"][0]["price"] == "14.99"


# raw JSON text, so the number reaches the server exactly as written
@pytest.mark.parametrize(
    "price_json",
    [
        "0.123456789012345678901",  # too many decimal places
        "14.999",  # too many decimal places
        '"14.999"',  # too many decimal places, as a string
        "1e999",  # becomes infinity
        "1e300",  # too large
        "1000000",  # too large
        '"cheap"',  # not a number
    ],
)
def test_add_menu_unsupported_price_returns_422(client: TestClient, menus_file: Path, price_json: str) -> None:
    body = '{"name": "Pho", "category": "Noodles", "price": ' + price_json + ', "is_available": true}'
    response = client.post(
        "/restaurants/rest_001/menu",
        content=body,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert json.loads(menus_file.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("menu_records", [UPDATE_MENUS])
@pytest.mark.parametrize("price", [3.99, "3.99"])
def test_update_menu_accepts_number_or_decimal_string_price(client: TestClient, menus_file: Path, price) -> None:
    response = client.patch(
        "/restaurants/rest_001/menu/menu_002",
        json={"price": price},
    )

    assert response.status_code == 200
    assert response.json()["price"] == "3.99"
    saved = json.loads(menus_file.read_text(encoding="utf-8"))
    assert saved[0]["items"][0]["price"] == "3.99"


@pytest.mark.parametrize("menu_records", [UPDATE_MENUS])
@pytest.mark.parametrize(
    "price_json",
    ["0.123456789012345678901", "3.999", "1e999", "1000000", '"cheap"'],
)
def test_update_menu_unsupported_price_returns_422(client: TestClient, menus_file: Path, price_json: str) -> None:
    response = client.patch(
        "/restaurants/rest_001/menu/menu_002",
        content='{"price": ' + price_json + "}",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert json.loads(menus_file.read_text(encoding="utf-8")) == UPDATE_MENUS


def test_main_app_returns_422_not_500_for_infinite_price(client: TestClient, menus_file: Path) -> None:
    # client wraps the real app in main.py, so this checks its 422 handler is registered
    response = client.post(
        "/restaurants/rest_001/menu",
        content='{"name": "Pho", "category": "Noodles", "price": 1e999, "is_available": true}',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "price"]
    assert json.loads(menus_file.read_text(encoding="utf-8")) == []


@pytest.mark.parametrize("price", [0, "0", "0.00"])
def test_add_menu_free_item_returns_201(client: TestClient, menus_file: Path, price) -> None:
    response = client.post(
        "/restaurants/rest_001/menu",
        json={"name": "Free sample", "category": "Samples", "price": price, "is_available": True},
    )

    assert response.status_code == 201
    assert Decimal(response.json()["price"]) == Decimal("0")
    saved = json.loads(menus_file.read_text(encoding="utf-8"))
    assert Decimal(saved[0]["items"][0]["price"]) == Decimal("0")


@pytest.mark.parametrize("menu_records", [UPDATE_MENUS])
@pytest.mark.parametrize(
    "path",
    [
        "/restaurants/rest_01/menu/menu_002",  # restaurant ID too short
        "/restaurants/rest_0001/menu/menu_002",  # restaurant ID too long
        "/restaurants/rest_001/menu/menu_02",  # menu item ID too short
        "/restaurants/rest_001/menu/menu_0002",  # menu item ID too long
    ],
)
def test_update_menu_bad_id_length_returns_422(client: TestClient, menus_file: Path, path: str) -> None:
    response = client.patch(path, json={"price": 3.99})

    assert response.status_code == 422
    assert json.loads(menus_file.read_text(encoding="utf-8")) == UPDATE_MENUS


@pytest.mark.parametrize("bad_id", ["rest_01", "rest_0001", "r"])
def test_get_menu_bad_restaurant_id_length_returns_422(client: TestClient, bad_id: str) -> None:
    assert client.get(f"/restaurants/{bad_id}/menu").status_code == 422


@pytest.mark.parametrize(
    "broken_menus",
    [
        "not json",  # file is not valid JSON
        '{"restaurant_id": "rest_001"}',  # file is not a list
        '[{"restaurant_id": "rest_001", "currency": "CAD", "items": [{"id": "item_001"}]}]',  # item missing fields
    ],
)
def test_get_menu_unreadable_menu_data_returns_500_with_detail(
    client: TestClient, menus_file: Path, broken_menus: str
) -> None:
    # Regression: MenuReadError used to escape the route as an unexplained 500
    menus_file.write_text(broken_menus, encoding="utf-8")

    response = client.get("/restaurants/rest_001/menu")

    assert response.status_code == 500
    assert response.json() == {"detail": "Unable to read menu data"}
