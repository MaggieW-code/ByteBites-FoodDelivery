# api

## Purpose

The only frontend code that talks to the backend. Each function wraps one endpoint, so
pages and components call a typed function instead of `fetch`.

## Contents

| File | Functions → endpoint | Used by |
|---|---|---|
| `restaurants.ts` | `fetchRestaurants(cuisine?)` → `GET /restaurants`, `fetchRestaurantById` → `GET /restaurants/{id}`, `createRestaurant` → `POST /restaurants`, `updateRestaurant` → `PATCH /restaurants/{id}` | `DiscoverView`, `RestaurantDetailsView`, `CreateRestaurantForm`, `UpdateRestaurantForm` |
| `menus.ts` | `fetchMenu(restaurantId, signal?)` → `GET /restaurants/{id}/menu` | `RestaurantMenuView` |

## How it connects

- Calls the FastAPI routes in `backend/app/routes/`; a change to a path, status code, or
  response model there changes this folder.
- Returns types from `types/`. Throws an `Error` on any non-2xx response; callers catch it
  and show a message.

## Conventions

- One file per backend feature, named after it (`restaurants.ts`).
- Every function encodes path parameters with `encodeURIComponent`, checks
  `response.ok`, and returns a typed promise.
- Read functions accept an optional `AbortSignal` so a page can cancel stale requests.
- Not yet true:
  - The base URL is hardcoded in each file (F15).
  - Request types live here instead of `types/` (F16).
  - Errors are handled three different ways, user-facing text is written here, and
    `createRestaurant` / `updateRestaurant` show the backend's raw response body to the
    user (F30).
- Proposed: one `client.ts` with the base URL and a
  fetch wrapper that throws a typed `ApiError` (status + backend error `code`). The UI picks
  the words, which is also what localization needs.
