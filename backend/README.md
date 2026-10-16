## Tech Stack
- FastAPI - Backen API for HTTP requests
- CORS (Cross-Origin Resource Sharing) handles protocol communication from different origins.
- pytest - handles unit tests
## Restaurant details API

`GET /restaurants/{restaurant_id}` reads through the service and repository
from the existing restaurant JSON file. It returns the `Restaurant` model
(`id`, `name`, `cuisine`, `rating`, `address`, `is_active`).

- **200:** matching restaurant, e.g. `/restaurants/rest_001`.
- **404:** well-formed identifier with no matching record; response example:
  `{"detail": "Restaurant 'rest_999' not found"}`.
- **422:** identifier is not exactly eight characters, matching the model's ID
  constraint.
- **500:** storage or invalid persisted-data failures; these are not translated
  into restaurant-not-found responses.

FastAPI documents this endpoint at `/docs`. Run `python3 -m pytest -q` from the
repository root. Details tests use temporary JSON files rather than application
data and cover repository lookup, service results, unknown identifiers, response
fields, identifier validation, storage failures, and the OpenAPI response schema.

## Restaurant menu API

`GET /restaurants/{restaurant_id}/menu` retrieves the selected restaurant's
menu through route → service → repository → JSON. Restaurant existence uses the
existing repository ID lookup. Sample data lives in `backend/app/data/menus.json`.

The Pydantic `Menu` response includes `restaurant_id`, `currency`, and `items`.
Each `MenuItem` includes `id`, `name`, `description`, `price` (a decimal
string), and `is_available`. Items belong to their enclosing restaurant menu.
Menu JSON is assumed to have valid records and unique identifiers.

Responses: 200 for a menu (empty items for a known restaurant without a menu),
404 for an unknown restaurant and 422 for a non-eight-character ID. Empty menus default to CAD. See `/docs`.

Run isolated menu tests with `python3 -m pytest backend/tests/test_menu.py -v`.
