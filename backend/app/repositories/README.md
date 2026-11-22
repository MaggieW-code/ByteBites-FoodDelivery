# repositories

## Purpose

The only layer that reads or writes `data/`. Each repository hides one JSON file behind
plain methods, so services never see file paths or the file format.

## Contents

| File | File it owns | Methods | Errors it raises |
|---|---|---|---|
| `restaurant_repository.py` | `restaurants.json` | `get_all`, `get_by_id`, `create`, `update` | `RestaurantDataNotFoundError`, `RestaurantDataMalformedError`, `RestaurantDataError` |
| `menu_repository.py` | `menus.json` | `get_all`, `get_by_restaurant_id`, `find_item`, `add`, `update` | `MenuDataNotFoundError`, `MenuDataMalformedError`, `MenuDataError` |

The three errors mean: the file is missing, the file isn't valid JSON, the top level isn't a list.

## How it connects

- Called by `services/`. `MenuService` uses both repositories (it checks the restaurant
  exists before returning a menu).
- Takes its file path in the constructor (`Repository(data_path)`), so tests pass a
  `tmp_path` file.
- Writes load the whole file, change the list in memory, and write the whole file back.

## Conventions

- One repository per data file. No HTTP errors, no business rules.
- Return Pydantic models from `models/`, validated on load; accept models on save.
- Raise the repository's own data errors on storage failures; return `None` when a lookup
  finds nothing, and let the service decide what "not found" means.
- Not yet true: reads return raw `dict`s, `update` in `restaurant_repository.py`
  decides which fields may change, and `menu_repository.py` `get_by_restaurant_id` skips
  `get_all`'s error handling.
