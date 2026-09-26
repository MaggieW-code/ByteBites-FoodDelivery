# Food Delivery

Food Delivery is a COSC 310 university team project. The application will
eventually support restaurant discovery, menus, customer accounts, carts,
checkout, orders, delivery management, and reporting. Feature development will
be incremental; this repository currently contains the initial backend
foundation only.

## Technology stack

- Python
- FastAPI and Uvicorn
- Pydantic (provided by FastAPI)
- pytest and FastAPI `TestClient`
- JSON persistence (no database)
- Git and GitHub

## Current status

The project has a minimal FastAPI application with a `GET /health`, `GET/restaurants` endpoint,
pytest coverage for that endpoint, and the initial layered architecture
scaffolding. Application features have not been implemented yet.

## Architecture overview

The planned architecture is:

**Frontend → FastAPI Routes → Services → Repositories → JSON Persistence**

Routes handle HTTP concerns, services contain business logic, and repositories
hide persistence details. See [docs/architecture.md](docs/architecture.md) for
the layer responsibilities.

### Naming Convention for Branches:
`name/feature/short-description-here`

## Repository structure

```text
main.py
backend/
├── app/
│   ├── routes/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   └── data/
└── tests/
frontend/
docs/
└── architecture.md
```

## Backend setup

From the repository root, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Start FastAPI

From the repository root, with the virtual environment activated:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. 

## Endpoints

- `GET /health` — returns `{"status": "ok"}` to confirm the API is running.
- `GET /restaurants` — returns the list of restaurants, each with `id`,
  `name`, `cuisine`, `rating`, `address`, and `is_active`. The bundled
  `backend/app/data/restaurants.json` file ships with representative sample
  data, so this endpoint works out of the box.

## Run tests

From the repository root, with the virtual environment activated:

```bash
pytest
```

Tests use in-memory HTTP requests through FastAPI's `TestClient`; they do not
modify application data.

## Configurable

Restaurant data is stored as JSON at `backend/app/data/restaurants.json` by default.

You can change this by setting the `RESTAURANT_TRIAL_PATH` environment variable
to a different file path. This is useful for testing, since tests can point
to their own temporary data file instead of using the real one.

## Team development workflow

For each change, follow:

**GitHub Issue → Feature Branch → Implementation + Tests → Pull Request →
Peer Review → Merge**

Implementation work should not be committed directly to `main`. Keep changes
focused, include tests for changed behavior, and use pull requests for review.
`name/feature/short-description-of-ticket`