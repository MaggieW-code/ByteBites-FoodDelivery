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
| Shared fixtures | `conftest.py` |
| Feature folders | `auth/`: accounts, sign-in, sessions (see its README). New features get a folder; older files move in a later refactor |

## How it connects

- `pytest.ini` at the repo root sets `pythonpath = .`, so tests import `backend.app...` and
  `main`. Run from the repo root: `.venv/bin/pytest backend/tests`.
- `conftest.py` holds the shared fixtures; pytest loads it automatically. The chain is
  `<feature>_records` → `<feature>s_file` (in `tmp_path`) → `<feature>_repository` →
  `<feature>_service` → `client`.
- `client` points both routers at this test's services with `monkeypatch.setattr` and returns
  one `TestClient` on `main.app` that is shared for the whole session (`session_client`). The
  client holds no data; every test still gets fresh files.
- CI runs this suite on PRs into `main`.

## Conventions

- Test the layer below through its public methods. Model tests check validation, repository
  tests check the file round trip, service tests check business rules and domain errors,
  route tests check status codes and response bodies.
- Isolation: data goes in `tmp_path`, environment variables are set with
  `monkeypatch.setenv`, and module attributes are swapped with `monkeypatch.setattr`. Never
  assign `os.environ` or module globals directly.
- Replace the whole service in route tests, not a repository's internal `data_path`.
- Fixtures shared by more than one file belong in `conftest.py`, not copied between files.
- Route tests take the `client` fixture; don't build a `TestClient` or patch routes in a test.
- To change a test's data, override the records fixture: in the file for every test there,
  or with `@pytest.mark.parametrize("<feature>_records", [...])` for one test.
- Only data-free, read-only objects get `scope="session"`. Data fixtures stay per test.
- Proposed: after F1's `Depends`, only `client` changes, to `app.dependency_overrides`.
