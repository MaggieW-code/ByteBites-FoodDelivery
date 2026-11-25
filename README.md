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
    ├── hooks/
    ├── layouts/
    ├── lib/
    ├── pages/
    ├── routes/
    └── types/
docs/
├── README.md
├── agent_usage.md
├── architecture.md
├── architecture_improvements.md
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
npm run test
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
  `category`, `price` (0 or more), `is_available`, and optional
  `description`. Returns `201` with the created item, including its
  generated `id`. Returns `404` if the restaurant does not exist and `422` if
  `restaurant_id` is not 8 characters; nothing is saved in either case.
- `PATCH /restaurants/{restaurant_id}/menu/{menu_item_id}` — updates any of
  `name`, `category`, `price`, or `is_available`. Returns `404` if the menu
  item does not exist for that restaurant and `422` if `restaurant_id` or
  `menu_item_id` is not 8 characters; nothing is saved in either case.

### Customers

- `POST /customers` — registers a customer. Body: `full_name`, `email`,
  `phone` (all required; `email` must be a valid address; `phone` must be a real Canadian number in
  any common format, e.g. `(250) 222-1234`, and is returned as `+12502221234`) and
  `password` (8–128 characters).
  Returns `201` with the new customer (`id`, `full_name`, `email`, `phone`,
  `is_active`, `role`, `delivery_addresses`), never the password. A `role`
  in the body is ignored: this endpoint only creates customers. Returns
  `409` if the email is already registered (emails are trimmed and
  lowercased first). Sign in afterwards with `POST /auth/sign-in`.
- `GET /customers/me` — the signed-in customer's own profile (same shape as
  above). Send `Authorization: Bearer <token>`. Returns `401` without a valid
  token and `403` for a non-customer or a deactivated account.
- `PATCH /customers/me` — update the signed-in customer. Send only the fields to
  change: `full_name`, `email`, `phone`. Same rules as registration. Returns
  `200` with the updated profile, `409` if the email belongs to another account,
  and `422` for an empty body, a `null`, or an invalid value. `role`,
  `is_active`, `password` and addresses can't be changed here.
- `POST /customers/me/addresses` — add a delivery address (`label`, `address`).
  Returns `201` with the address and its new 8-character `id`.
- `PATCH /customers/me/addresses/{address_id}` — change one address; send only
  `label` and/or `address`. Returns `200`, or `404` if the customer has no
  address with that ID.
- `DELETE /customers/me/addresses/{address_id}` — remove one address. Returns
  `204`, or `404`. A customer can only reach their own addresses.
- `POST /customers/me/deactivate` — deactivate the signed-in customer and sign
  them out on every device. Returns `204`. Afterwards their tokens get `401`
  and signing in again gets `403`.

Request bodies that fail validation return `422`.

Prices are exact decimals: they are stored in `menus.json` and returned by the
API as strings (e.g. `"14.99"`). A request may send the price as a number
(`14.99`) or a decimal string (`"14.99"`). It must be 0 or more (0 is a free
item), have at most 2 decimal places, and be at most `999999.99`. Anything
else (for example `-1`, `14.999`, `1e999` or `"cheap"`) returns `422` and nothing is saved.

Menu item IDs are unique across all restaurants. New IDs are checked against
every menu before they are saved.

### Menu item lookup (for Cart and Checkout)

`MenuService.get_menu_item(menu_item_id)` finds a menu item using only its ID
and returns a `MenuItem` with its current `price` (`Decimal`), `is_available`,
`name`, and `restaurant_id`. Cart and Checkout use it to validate items and get
current prices. It is a service method, not an HTTP endpoint. It raises:

- `MenuItemNotFoundError` if no item has that ID
- `MenuRestaurantNotFoundError` if the item's restaurant does not exist
- `MenuRestaurantInactiveError` if the item's restaurant is not active
- `MenuDataIntegrityError` if more than one item in `menus.json` has that ID

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
