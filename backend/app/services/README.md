# services

## Purpose

Business logic: rules, validation that depends on stored data, ID generation, defaults, and
workflow. Services can be tested without HTTP or real files.

## Contents

| File | Methods | Domain errors |
|---|---|---|
| `restaurant_service.py` | `get_restaurants(cuisine)` (case-insensitive filter), `get_restaurant_by_id`, `create_restaurant` (new 8-char ID, `rating=0.0`, `is_active=True`), `update_restaurant` | `RestaurantNotFoundError` |
| `menu_service.py` | `get_menu` (empty CAD menu if none stored), `add_menu` (new 8-char ID), `update_menu` | `MenuRestaurantNotFoundError`, `MenuItemNotFoundError` |

## How it connects

- Called by `routes/`, which translate domain errors into HTTP status codes.
- Call `repositories/` for storage and receive repositories in the constructor, so tests
  pass repositories pointed at `tmp_path` files.
- Take request models from `models/` and return stored models.
- `MenuService` also uses `RestaurantRepository` to check a restaurant exists (the one
  documented cross-feature exception). New cross-feature access goes through the other
  feature's service.

## Conventions

- Raise a named domain error for every business failure (`<Noun>NotFoundError`,
  `<Noun>ValidationError`); never `HTTPException`, never a bare `ValueError`.
- Return models, not `dict`s. "Not found" is an exception, not a `None` return.
- Business defaults and rules (ID format, starting rating, default currency, which fields are
  editable) live here or on the models, nowhere else.
- No file paths, no `open`, no `json`.
- Not yet true: services convert repository dicts with `Model(**record)`;
  `update_restaurant` raises `ValueError` and returns `None` for not-found; `add_menu` doesn't
  check the restaurant exists (#123); `update_menu` saves prices as `float`.
