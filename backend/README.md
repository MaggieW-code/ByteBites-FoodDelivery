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
