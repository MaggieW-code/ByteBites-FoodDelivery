# data

## Purpose

JSON files that stand in for a database. Only repositories know these files exist: they
read and write them, and validate every record against a Pydantic model in `models/`.

## Contents

| File | Shape | Read by |
|---|---|---|
| `restaurants.json` | List of restaurants: `id`, `name`, `cuisine`, `rating`, `address`, `is_active` | `RestaurantRepository` |
| `menus.json` | List of menus, one per restaurant: `restaurant_id`, `currency`, `items[]` (`id`, `name`, `description`, `price` as a string, `is_available`) | `MenuRepository` |
| `menu_items.json` | Flat list of menu items | Nothing. Unused, scheduled for deletion in #122 |

## How it connects

- Repositories load and save whole files and hand model objects to services; services and
  routes never see file paths or the file format.
- File paths come from `config.py`, so tests and deployments can point elsewhere.
- Not yet true: routes build repositories with hardcoded paths
  (`routes/restaurant_routes.py`, `routes/menu_routes.py`), `config.py` paths are unused,
  and repositories return raw dicts instead of validated models.
- Tests never touch these files. They write their own copies to pytest's `tmp_path`.

## Conventions

- IDs are 8-character prefixed strings (`rest_001`, `item_001`).
- Prices are stored as strings so they load back as exact `Decimal` values.
- Every `restaurant_id` in `menus.json` must exist in `restaurants.json`.
