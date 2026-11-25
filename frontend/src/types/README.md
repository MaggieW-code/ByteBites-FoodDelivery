# types

## Purpose

TypeScript types that mirror the backend's Pydantic models, so frontend code knows the shape
of every request and response.

## Contents

| File | Types | Mirrors |
|---|---|---|
| `restaurant.ts` | `Restaurant` | `backend/app/models/restaurant_model.py` `Restaurant` |
| `menu.ts` | `Menu`, `MenuItem` | `backend/app/models/menu_model.py` (the `GET` menu shape) |
| `restaurantCard.ts` | `RestaurantCardProps` | Nothing: props for the unused `RestaurantCard` component |

## How it connects

- `api/` declares its return types with these; pages, components, hooks, and `lib/` use them.
- Each type changes in the same PR as the backend model it mirrors (vertical stack).
- Types are erased at runtime: `response.json()` is not checked against them, and nothing
  type-checks the code until TypeScript is installed (F29).

## Conventions

- One file per backend feature; one type per backend model, same name.
- Field names match the JSON exactly, so they stay snake_case (`is_active`, `restaurant_id`).
- `Decimal` fields arrive as strings (`price: string`); convert only for display.
- Use `type`, not `interface`. Request bodies are `Create<Noun>Request` / `Update<Noun>Request`.
- Not yet true: restaurant request types live in `api/restaurants.ts`, menu
  request types don't exist yet, and `restaurantCard.ts` is component props, not a mirror
  (F16, F28).
- Proposed: generate this folder from the backend's
  OpenAPI schema with `openapi-typescript`, so nobody keeps it in sync by hand.
