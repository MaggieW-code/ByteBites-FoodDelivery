# app

## Purpose

The backend application package. It holds every backend layer plus the app's configuration.
`main.py` at the repo root builds the FastAPI app from it.

## Contents

| Path | Role |
|---|---|
| `routes/` | HTTP layer: one router per feature |
| `services/` | Business rules and domain errors |
| `repositories/` | The only code that reads or writes `data/` |
| `models/` | Pydantic models shared by every layer |
| `data/` | JSON files that stand in for a database |
| `config.py` | Settings read from environment variables, with defaults. `get_restaurant_data_path()` returns the restaurant data file (`RESTAURANT_TRIAL_PATH`, else `data/restaurants.json`) |

Each folder has its own README with the details.

## How it connects

- `main.py` imports each `routes/*` router and registers it. Nothing else imports from
  outside this package.
- Requests flow `routes → services → repositories → data`. `models/` is imported by all of
  them and imports none of them.
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
  - Nothing in the app calls `config.py`. Routes hardcode their own data paths (F1, F2, F3).
  - `config.py` covers only the restaurant file, and its `ValueError` check can never
    trigger (F22).
