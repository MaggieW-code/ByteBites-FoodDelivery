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
- JSON/CSV persistence (planned; no database)
- Git and GitHub

## Current status

The project has a minimal FastAPI application with a `GET /health` endpoint,
pytest coverage for that endpoint, and the initial layered architecture
scaffolding. Application features have not been implemented yet.

## Architecture overview

The planned architecture is:

**Frontend → FastAPI Routes → Services → Repositories → JSON/CSV Persistence**

Routes handle HTTP concerns, services contain business logic, and repositories
hide persistence details. See [docs/architecture.md](docs/architecture.md) for
the layer responsibilities.

### Naming Convention for Branches:
`name/feature/short-description-here`

## Repository structure

```text
backend/
├── app/
│   ├── main.py
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
uvicorn backend.app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Check
`http://127.0.0.1:8000/health` for the initial health response.

## Run tests

From the repository root, with the virtual environment activated:

```bash
pytest
```

Tests use in-memory HTTP requests through FastAPI's `TestClient`; they do not
modify application data.

## Team development workflow

For each change, follow:

**GitHub Issue → Feature Branch → Implementation + Tests → Pull Request →
Peer Review → Merge**

Implementation work should not be committed directly to `main`. Keep changes
focused, include tests for changed behavior, and use pull requests for review.
`name/feature/short-description-of-ticket`