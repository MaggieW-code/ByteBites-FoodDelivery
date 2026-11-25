# api

## Purpose

The only frontend code that talks to the backend. Each function wraps one endpoint, so
pages and components call a typed function instead of `fetch`.

## Contents

| File | Functions → endpoint | Used by |
|---|---|---|
| `restaurants.ts` | `fetchRestaurants(cuisine?)` → `GET /restaurants`, `fetchRestaurantById` → `GET /restaurants/{id}`, `createRestaurant` → `POST /restaurants`, `updateRestaurant` → `PATCH /restaurants/{id}` | `DiscoverView`, `RestaurantDetailsView`, `CreateRestaurantForm`, `UpdateRestaurantForm` |
| `client.ts` | `API_BASE_URL` (env `API_BASE_URL`, default `http://127.0.0.1:8000`), `request<T>()` (JSON, `response.ok` check, throws `ApiError`), `ApiError` (`status`, `detail`, `fieldErrors` for 422) | `accounts.ts` |
| `accounts.ts` | `registerCustomer` → `POST /customers`, `signIn` → `POST /auth/sign-in` (stores the token in `localStorage`), `getCurrentAccount(token)` → `GET /auth/me`, `signOut` → `POST /auth/sign-out` (always forgets the token, even if the backend is down), `getAccessToken`, `clearAccessToken` | `AccountView`, `useCurrentAccount`, `GenericLayout` |
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
  - `restaurants.ts` and `menus.ts` still hardcode the base URL and handle errors their own way; new
    files use `client.ts`, and the old ones move to it in a follow-up (F15, F30).
  - Request types live here instead of `types/` (F16).
  - Errors are handled three different ways, user-facing text is written here, and
    `createRestaurant` / `updateRestaurant` show the backend's raw response body to the
    user (F30).
- Proposed: one `client.ts` with the base URL and a
  fetch wrapper that throws a typed `ApiError` (status + backend error `code`). The UI picks
  the words, which is also what localization needs.
