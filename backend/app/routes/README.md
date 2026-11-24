# routes

## Purpose

The HTTP layer. Each route parses the request, calls one service method, and returns the
response with its status code. Routes turn domain errors into HTTP errors and hold no
business logic and no file access.

## Contents

| File | Endpoints | Service | Errors → status |
|---|---|---|---|
| `health.py` | `GET /health` | none | none |
| `restaurant_routes.py` | `GET /restaurants?cuisine=`, `GET /restaurants/{restaurant_id}`, `POST /restaurants` (201), `PATCH /restaurants/{restaurant_id}` | `RestaurantService` | `RestaurantNotFoundError` → 404 |
| `menu_routes.py` | `GET /restaurants/{restaurant_id}/menu`, `POST /restaurants/{restaurant_id}/menu` (201), `PATCH /restaurants/{restaurant_id}/menu/{menu_item_id}` | `MenuService` | `MenuRestaurantNotFoundError` → 404, `MenuItemNotFoundError` → 404 |
| `auth_routes.py` | `POST /auth/sign-in`, `GET /auth/me`, `POST /auth/sign-out` (204, also for unknown tokens) | `AuthService` | `InvalidCredentialsError` → 401 with `WWW-Authenticate: Bearer`, `AccountDeactivatedError` → 403. Token errors come from `dependencies/auth.py` |

Each file exposes a `router` that `main.py` registers with `app.include_router`.

## How it connects

- `main.py` (repo root) registers every router. A new feature's router is not reachable
  until it is added there.
- Routes call `services/` only, never `repositories/`.
- `auth_routes.py` receives its service with `Depends(get_auth_service)` from `dependencies/`,
  which builds it from `config.py` paths. Routes never construct services or repositories.
  Protected routes declare `get_current_account` or `require_role(...)` from the same place.
- Request bodies and responses are typed with `models/`, so FastAPI rejects bad input with a
  422 before the route runs and builds `/docs` from the same models.
- Tests reach the routes through `TestClient(app)` and swap in a service built on `tmp_path`
  files: `monkeypatch.setitem(app.dependency_overrides, get_auth_service, ...)` for auth, and
  `monkeypatch.setattr(<routes module>, "<feature>_service", ...)` for the older routes.
- `frontend/src/api/` calls these endpoints. Changing a path, status code, or response model
  changes the frontend contract.

## Conventions

- One file per feature, named `<feature>_routes.py`, with one module-level `router`.
- Every route declares `response_model`, a `description`, and its error codes in
  `responses={...}`. Creates return 201.
- Catch only the named domain errors the service raises and re-raise as
  `HTTPException(status_code=..., detail=str(error)) from error`. Never catch `ValueError`
  or `Exception`. Storage errors from repositories are left to become a 500.
- Validate ID path parameters on every route that takes them, not only the `GET` routes.
  Reuse the ID type from `models/` and only add a description:
  `restaurant_id: Annotated[RestaurantId, Path(description=...)]`. Don't write
  `restaurant_id: RestaurantId = Path(...)`: FastAPI then silently drops the 8-character rule.
- Not yet true:
  - Restaurant and menu routes build their own repositories and know where `data/` is
    (F1, F2). `auth_routes.py` shows the target: `Depends` on a provider in `dependencies/`.
    `restaurant_routes.py` uses a path relative to the working directory.
  - `PATCH /restaurants/{id}` catches `ValueError` and checks for `None` (F17).
  - Only the `GET` detail and menu routes validate `restaurant_id`. `menu_item_id` is
    never validated (F20).
  - Error handling is inconsistent across routes (F21): `POST .../menu` handles no errors,
    `PATCH .../menu/{id}` hardcodes its message and drops `from error`, and only two
    routes document their 404 in `responses`.

auth_routes.py provides POST /auth/sign-in, GET /auth/me, and POST /auth/sign-out.
order_routes.py uses the shared CurrentCustomer dependency for order details and history.
