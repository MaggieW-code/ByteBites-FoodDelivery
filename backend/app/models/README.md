# models

## Purpose

Pydantic models that define the shape of every piece of data in the backend: what clients
may send, what is stored, and what the API returns. A model is the single check that data
is valid.

## Contents

| File | Models | Role |
|---|---|---|
| `restaurant_model.py` | `Restaurant` | Stored record and API response |
| | `CreateRestaurantRequest`, `UpdateRestaurantRequest` | Request bodies for `POST` / `PATCH` |
| `menu_model.py` | `Menu`, `MenuItem` | A restaurant's menu as stored in `menus.json` and returned by `GET .../menu`. Price is `Decimal` |
| `menu_item_model.py` | `CreateMenuItem`, `MenuItem` | Request body and response for adding a menu item. Price is `float` |
| `update_menu_item_model.py` | `UpdateMenuItem` | Request body for updating a menu item |

Two different classes are named `MenuItem` (`menu_model.py` and `menu_item_model.py`). #122
merges the menu models into one file.

## How it connects

Models are the shared vocabulary of the backend, so every layer uses them, but they depend on
no layer:

```
routes ──► services ──► repositories ──► data/
   │           │             │
   └───────────┴──────┬──────┘
                      ▼
                   models/   (imports only pydantic and the standard library)
```

- **Routes** use request models as body types and stored models as `response_model`.
  FastAPI returns 422 for invalid input before any service code runs, and builds `/docs` from
  them.
- **Services** receive request models, apply business rules, and return stored models.
- **Repositories** validate file records into stored models on load and dump them on save.
- **Frontend** `frontend/src/types/` mirrors every model here by hand (stored, request, and
  response), one TypeScript type per model with the same name and fields. A model change and
  its type change go in the same PR.

## Conventions

- Models never import from `routes/`, `services/`, or `repositories/`.
- One file per feature holds all of that feature's models (`restaurant_model.py` is the
  reference).
- Naming: the stored model is the plain noun (`Restaurant`); request bodies are
  `Create<Noun>Request` and `Update<Noun>Request`.
- Every field uses `Field(strict=True, ...)` with explicit limits. IDs are exactly 8
  characters. Update models make every field optional (`None` means "don't change").
- Money is `Decimal`, never `float`.
- Proposed (after #122): frontend types will be generated from these models instead
  of copied by hand. FastAPI's `/openapi.json` → `openapi-typescript` → `frontend/src/types/api.ts`,
  called through `openapi-fetch` in `frontend/src/api/`. CI regenerates and fails on any diff,
  so a model change without regenerated types can't merge. Every route needs a
  `response_model` for its type to be generated.
- Not yet true: `menu_item_model.py` and `update_menu_item_model.py` use `float`
  prices and skip the `Request` suffix, and `menu_model.py` has no field constraints.
