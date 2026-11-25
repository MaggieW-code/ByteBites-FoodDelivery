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

`POST /restaurants/{restaurant_id}/menu` follows the same rules: 201 with the
created item, 404 for an unknown restaurant and 422 for a non-eight-character
ID. Nothing is saved on 404 or 422. `PATCH .../menu/{menu_item_id}` also returns
422 when the restaurant ID or menu item ID is not 8 characters.

Prices (POST and PATCH) may be a number or a decimal string, must be 0 or more
(0 is a free item), have at most 2 decimal places and be at most 999999.99; otherwise 422.
New item IDs are unique across all menus.

`MenuService.get_menu_item(menu_item_id)` looks up a single item by ID across
all menus for callers that need a lookup by item ID. It returns a `MenuItem` (price as `Decimal`,
availability, restaurant ID) and raises `MenuItemNotFoundError`,
`MenuRestaurantNotFoundError`, or `MenuRestaurantInactiveError`. If
`menus.json` has the same item ID more than once, it raises
`MenuDataIntegrityError` instead of guessing (the repository's
`DuplicateMenuItemIdError` never leaves the service).

Run isolated menu tests with `python3 -m pytest backend/tests/test_menu.py -v`.

## Shopping cart

The cart uses bearer authentication to identify the customer. Each customer
can have one active cart, and all items must come from the same restaurant.
Adding an item requires an active restaurant and an available menu item.

`CartService` calculates totals using current menu prices. Customers can
still view their cart after the restaurant is deactivated. Removing the last
item or clearing the cart resets its restaurant association. `CartRepository`
stores carts in `backend/app/data/carts.json`, which it creates on the first write.
