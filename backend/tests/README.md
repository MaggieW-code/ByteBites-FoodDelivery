# tests

## Purpose

Pytest suite for the backend. Every behaviour change ships with tests here. Tests never read
or write the real files in `backend/app/data/`.

## Contents

Most files are named `test_<feature>_<layer>.py`. Older user-story files test several layers
in one file.

| Layer | Files |
|---|---|
| Models | `test_restaurant_model.py`, `test_menu_item_model.py`, `test_update_menu_item_model.py` |
| Repositories | `test_restaurant_repository.py`, `test_menu_repository.py` |
| Services | `test_restaurant_service.py`, `test_menu_service.py` |
| Routes (HTTP) | `test_restaurant_routes.py`, `test_restaurant_management.py`, `test_menu_routes.py`, `test_health_routes.py` |
| One user story across layers | `test_restaurant_details.py`, `test_restaurant_cuisine_filter.py`, `test_menu.py` |
| Config | `test_config.py` |

## How it connects

- `pytest.ini` at the repo root sets `pythonpath = .`, so tests import `backend.app...` and
  `main`. Run from the repo root: `.venv/bin/pytest backend/tests`.
- Each test writes its own JSON to pytest's `tmp_path` and builds repositories on it.
- Route tests use `fastapi.testclient.TestClient` on `main.app` (or a small app with one
  router) and replace the route module's service with
  `monkeypatch.setattr(<feature>_routes, "<feature>_service", service)`.
- CI runs this suite on PRs into `main`.

## Conventions

- Test the layer below through its public methods. Model tests check validation, repository
  tests check the file round trip, service tests check business rules and domain errors,
  route tests check status codes and response bodies.
- Isolation: data goes in `tmp_path`, environment variables are set with
  `monkeypatch.setenv`, and module attributes are swapped with `monkeypatch.setattr`. Never
  assign `os.environ` or module globals directly.
- Replace the whole service in route tests, not a repository's internal `data_path`.
- Fixtures shared by more than one file belong in a `conftest.py`, not copied between files.
- Not yet true:
  - Two tests in `test_restaurant_routes.py` read the real `restaurants.json` and fail when
    pytest runs from another folder (F23).
  - Route tests use three different ways to swap in test data, and fixtures are copied
    between files (F24).
  - `test_config.py` sets `os.environ` directly (F25).
- Proposed (first, before other fixes): a shared `conftest.py` with `tmp_path` data
  fixtures and one `client` fixture fixes F23–F25. Later, F1's `Depends` changes only that
  fixture to use `app.dependency_overrides`.
