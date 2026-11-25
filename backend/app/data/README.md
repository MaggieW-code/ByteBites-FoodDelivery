# data

## Purpose

JSON files that stand in for a database. Only repositories know these files exist: they
read and write them, and validate every record against a Pydantic model in `models/`.

## Contents

| File | Shape | Read by |
|---|---|---|
| `restaurants.json` | List of restaurants: `id`, `name`, `cuisine`, `rating`, `address`, `is_active` | `RestaurantRepository` |
| `menus.json` | List of menus, one per restaurant: `restaurant_id`, `currency`, `items[]` (`id`, `name`, `description`, `price` as a string, `is_available`) | `MenuRepository` |
| `accounts.json` | List of accounts: `id`, `full_name`, `email`, `phone`, `role`, `is_active`, `password_hash` (scrypt), plus `delivery_addresses` (each `{id, label, address}`) or `owned_restaurant_ids` by role. Demo seed data. A missing file is a 500, not "no accounts" | `AccountRepository` |
| `sessions.json` | List of sessions: `token_hash` (SHA-256, never the token), `account_id`, `created_at`, `expires_at`. Runtime data: created on first sign-in, gitignored | `SessionRepository` |

## How it connects

- Repositories load and save whole files and hand model objects to services; services and
  routes never see file paths or the file format.
- File paths come from `config.py`, so tests and deployments can point elsewhere.
- Not yet true (auth already follows these): restaurant and menu routes build repositories
  with hardcoded paths (`routes/restaurant_routes.py`, `routes/menu_routes.py`), their
  `config.py` path is unused, and those repositories return raw dicts instead of validated
  models.
- Tests never touch these files. They write their own copies to pytest's `tmp_path`.

## Conventions

- IDs are 8-character prefixed strings (`rest_001`, `item_001`).
- Prices are stored as strings so they load back as exact `Decimal` values.
- Every `restaurant_id` in `menus.json` must exist in `restaurants.json`.


## Demo accounts

For local demos and the TA only. Never reuse these passwords anywhere real.

| Email | Password | Role |
|---|---|---|
| `customer@example.com` | `demo-password-123` | customer |
| `owner@example.com` | `owner-password-1234` | restaurant_owner |
