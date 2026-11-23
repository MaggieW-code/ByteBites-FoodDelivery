# app

## Purpose

The backend application package. It holds every backend layer plus the app's configuration.
`main.py` at the repo root builds the FastAPI app from it.

## Contents

| Path | Role |
|---|---|
| `routes/` | HTTP layer: one router per feature |
| `dependencies/` | FastAPI dependencies routes declare with `Depends`: authentication (401) and role checks (403) |
| `services/` | Business rules and domain errors |
| `repositories/` | The only code that reads or writes `data/` |
| `models/` | Pydantic models shared by every layer |
| `data/` | JSON files that stand in for a database |
| `config.py` | Settings read from environment variables, with defaults. `get_restaurant_data_path()` (`RESTAURANT_TRIAL_PATH`), `get_accounts_data_path()` (`ACCOUNTS_PATH`), `get_sessions_data_path()` (`SESSIONS_PATH`), each defaulting to a file in `data/`; `get_auth_token_lifetime()` (`AUTH_TOKEN_TTL_MINUTES`, default 60, must be a positive whole number) |

Each folder has its own README with the details.

## How it connects

- `main.py` imports each `routes/*` router and registers it. Nothing else imports from
  outside this package.
- Requests flow `routes → services → repositories → data`. `models/` is imported by all of
  them and imports none of them.
- Protected routes run `dependencies/` before their own code. The auth dependency builds
  `AuthService` from `config.py` paths; tests swap it with `app.dependency_overrides`.
- `config.py` is meant to give repositories their file paths, so tests and deployments can
  point at other files.
- Tests live outside the package in `backend/tests/`.

## Conventions

- Imports are absolute from the repo root (`from backend.app.services... import ...`), so run
  `uvicorn`, `pytest`, and scripts from the repo root.
- Every setting lives in `config.py` and is read from an environment variable with a default.
  No other module reads `os.environ` or builds a path to `data/`.
- A new feature adds one file per layer (`<feature>_routes.py`, `<feature>_service.py`,
  `<feature>_repository.py`, `<feature>_model.py`) and registers its router in `main.py`.
- Not yet true:
  - Only the auth dependency calls `config.py`. Other routes hardcode their own data paths (F1, F2, F3).
  - `get_restaurant_data_path()`'s `ValueError` check can never trigger (F22).
