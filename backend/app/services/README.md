# services

## Purpose

Business logic: rules, validation that depends on stored data, ID generation, defaults, and
workflow. Services can be tested without HTTP or real files.

## Contents

| File | Methods | Domain errors |
|---|---|---|
| `restaurant_service.py` | `get_restaurants(cuisine)` (case-insensitive filter), `get_restaurant_by_id`, `create_restaurant` (new 8-char ID, `rating=0.0`, `is_active=True`), `update_restaurant` | `RestaurantNotFoundError` |
| `menu_service.py` | `get_menu` (empty CAD menu if none stored), `add_menu` (new 8-char ID), `update_menu` | `MenuRestaurantNotFoundError`, `MenuItemNotFoundError` |
| `accounts/auth_service.py` | `sign_in` (new random token, stores only its SHA-256, expires after `token_lifetime`), `resolve_token` → `AuthenticatedAccount`, `sign_out` | `InvalidCredentialsError` (same message for unknown email and wrong password), `AccountDeactivatedError`, `InvalidTokenError`, `SessionExpiredError`, all subclasses of `AuthError` |
| `accounts/account_service.py` | `register_account` (rejects a used email, picks a free 8-char ID, then builds the account with `AccountFactory`; default role `customer`), `get_account`, `update_customer` (customers only; changes only the fields sent, 409-style error if the new email belongs to another account, validates the merged record before saving), `add_address` (new ID unique within the customer), `update_address`, `remove_address`, `deactivate_account` (marks the account inactive and deletes all its sessions, so its tokens get 401 at once). Takes an `AccountRepository` and a `SessionRepository`. Returns public accounts (`to_public` drops `password_hash`) | `EmailAlreadyRegisteredError`, `AccountNotFoundError` (also for a non-customer on customer-only methods), `DeliveryAddressNotFoundError`, subclasses of `AccountError` |
| `accounts/account_factory.py` | `AccountFactory.create(request, role, account_id=...)`: builds the stored account through the `StoredAccount` union (the `role` picks the class), hashed password, `is_active=True`, role defaults (e.g. no delivery addresses). The hasher is injected | Pydantic `ValidationError` for an unknown role |
| `accounts/password_hashing.py` | `hash_password`, `verify_password` (scrypt, random salt, constant-time compare) | `MalformedPasswordHashError` |

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
  `update_restaurant` raises `ValueError` and returns `None` for not-found.

CheckoutService reads current menu prices, handles menu read errors, and saves the order before closing the cart.
