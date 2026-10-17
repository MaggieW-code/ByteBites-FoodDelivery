# Food Delivery

Food Delivery is a COSC 310 university team project. The application will
eventually support restaurant discovery, menus, customer accounts, carts,
checkout, orders, delivery management, and reporting. Feature development will
be incremental; this repository currently contains the initial backend
foundation and the first restaurant and menu features.

## Technology stack

- Python
- FastAPI and Uvicorn
- Pydantic (provided by FastAPI)
- pytest and FastAPI `TestClient`
- JSON persistence (no database)
- React and TypeScript (frontend, bundled with Parcel)
- Git and GitHub

## Current status

The following features are implemented, with pytest coverage:

- **Restaurant discovery:** list restaurants and view restaurant details.
- **Restaurant management:** create and update restaurants.
- **Menu browsing:** view a restaurant's menu.
- **Menu management:** add and update menu items.

The React frontend includes a landing page, a restaurant discovery list,
restaurant details and menu views, and forms for creating and updating
restaurants.

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
│       ├── restaurants.json
│       └── menus.json
└── tests/
frontend/
├── index.html
└── src/
    ├── api/
    ├── components/
    ├── layouts/
    ├── pages/
    ├── routes/
    └── types/
docs/
├── architecture.md
├── scrum.md
├── team-agreement.md
└── PROVENANCE.md
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

The API will be available at `http://127.0.0.1:8000`. Interactive API docs
are available at `http://127.0.0.1:8000/docs`.

## Frontend setup

From the repository root, with the backend running:

```bash
cd frontend
npm install
npm start
```

Parcel serves the app locally and prints the URL. See
[frontend/README.md](frontend/README.md) for more detail.

## Endpoints

### Health

- `GET /health` — returns `{"status": "ok"}` to confirm the API is running.

### Restaurants

- `GET /restaurants` — returns the list of restaurants, each with `id`,
  `name`, `cuisine`, `rating`, `address`, and `is_active`. The bundled
  `backend/app/data/restaurants.json` file ships with representative sample
  data, so this endpoint works out of the box.
- `GET /restaurants/{restaurant_id}` — returns one restaurant.
  `restaurant_id` must be 8 characters (e.g. `rest_001`). Returns `404` if
  the restaurant does not exist.
- `POST /restaurants` — creates a restaurant. Body: `name`, `cuisine`,
  `address` (all required, non-empty). Returns `201` with the created
  restaurant.
- `PATCH /restaurants/{restaurant_id}` — updates any of `name`, `cuisine`,
  or `address`. Returns `400` for invalid updates and `404` if the
  restaurant does not exist.

### Menus

- `GET /restaurants/{restaurant_id}/menu` — returns the restaurant's menu
  (`restaurant_id`, `currency`, `items`). A restaurant with no items returns
  an empty menu. Returns `404` if the restaurant does not exist.
- `POST /restaurants/{restaurant_id}/menu` — adds a menu item. Body: `name`,
  `category`, `price` (greater than 0), `is_available`, and optional
  `description`. Returns `201` with the created item, including its
  generated `id`.
- `PATCH /restaurants/{restaurant_id}/menu/{menu_item_id}` — updates any of
  `name`, `category`, `price`, or `is_available`. Returns `404` if the menu
  item does not exist for that restaurant.

Request bodies that fail validation return `422`.

## Run tests

From the repository root, with the virtual environment activated:

```bash
pytest
```

Tests use in-memory HTTP requests through FastAPI's `TestClient`; they do not
modify application data.

## Configurable

Restaurant data is stored as JSON at `backend/app/data/restaurants.json` by default.
Menus and their items are stored in `backend/app/data/menus.json`.

You can change this by setting the `RESTAURANT_TRIAL_PATH` environment variable
to a different file path. This is useful for testing, since tests can point
to their own temporary data file instead of using the real one.

## Team development workflow

For each change, follow:

**GitHub Issue → Feature Branch → Implementation + Tests → Pull Request →
Peer Review → Merge**

Implementation work should not be committed directly to `main`. Keep changes
focused, include tests for changed behavior, and use pull requests for review. Furthermore, branches
should be deleted after merge once all work is completed.
`name/feature/short-description-of-ticket`
