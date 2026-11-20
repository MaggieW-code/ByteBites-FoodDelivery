"""Shared fixtures: every test gets its own data files in tmp_path; the TestClient is shared."""

import json
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.app.repositories.menu_repository import MenuRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.routes import menu_routes, restaurant_routes
from backend.app.services.menu_service import MenuService
from backend.app.services.restaurant_service import RestaurantService
from main import app


@pytest.fixture
def write_json(tmp_path: Path) -> Callable[[str, Any], Path]:
    def _write(name: str, data: Any) -> Path:
        path = tmp_path / name
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    return _write


# Data: override in a test file, or per test with @pytest.mark.parametrize("<name>", [...])
@pytest.fixture
def restaurant_records() -> list[dict[str, Any]]:
    return [
        dict(id="rest_001", name="Sushi", cuisine="Japanese", rating=4.5, address="123 Main St", is_active=True),
        dict(id="rest_002", name="Pizza", cuisine="Italian", rating=4.0, address="456 Main St", is_active=True),
        dict(id="rest_003", name="Ramen", cuisine="Japanese", rating=4.2, address="789 Main St", is_active=True),
    ]


@pytest.fixture
def menu_records() -> list[dict[str, Any]]:
    return []


@pytest.fixture
def restaurants_file(write_json: Callable[[str, Any], Path], restaurant_records: list[dict[str, Any]]) -> Path:
    return write_json("restaurants.json", restaurant_records)


@pytest.fixture
def menus_file(write_json: Callable[[str, Any], Path], menu_records: list[dict[str, Any]]) -> Path:
    return write_json("menus.json", menu_records)


@pytest.fixture
def restaurant_repository(restaurants_file: Path) -> RestaurantRepository:
    return RestaurantRepository(restaurants_file)


@pytest.fixture
def menu_repository(menus_file: Path) -> MenuRepository:
    return MenuRepository(menus_file)


@pytest.fixture
def restaurant_service(restaurant_repository: RestaurantRepository) -> RestaurantService:
    return RestaurantService(restaurant_repository)


@pytest.fixture
def menu_service(menu_repository: MenuRepository, restaurant_repository: RestaurantRepository) -> MenuService:
    return MenuService(menu_repository, restaurant_repository)


# Built once per test session; it holds no data, so sharing it is safe
@pytest.fixture(scope="session")
def session_client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def client(
    session_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    restaurant_service: RestaurantService,
    menu_service: MenuService,
) -> TestClient:
    # Point both routers at this test's services; monkeypatch undoes it after the test
    monkeypatch.setattr(restaurant_routes, "restaurant_service", restaurant_service)
    monkeypatch.setattr(menu_routes, "menu_service", menu_service)
    # Cookies would otherwise carry over between tests on the shared client
    session_client.cookies.clear()
    return session_client
