# src

## Purpose

All frontend application code: the entry point, the router, and one folder per frontend
layer.

## Contents

| Path | Role |
|---|---|
| `index.tsx` | Entry point. Mounts `<App />` on `#root` and fails fast if it's missing |
| `App.tsx` | `BrowserRouter`, the `GenericLayout` wrapper, and every route (`/`, `/restaurants`, `/restaurants/:restaurantId`, `/manage/restaurants`, 404) |
| `api/` | The only code that calls the backend |
| `types/` | TypeScript types mirroring backend models |
| `hooks/` | Reusable React stateful logic |
| `lib/` | Plain data-in, data-out functions |
| `components/` | Reusable UI pieces |
| `pages/` | Top-level views, one per route |
| `layouts/` | Shared page frame (header, navigation) |
| `routes/` | Meant for URL-to-page routing; currently holds only unused code |

## How it connects

- Flow: `App.tsx` routes a URL to a page → the page uses hooks, `lib/`, and components →
  data comes from `api/` → typed with `types/`.
- Dependencies point one way: `pages → components / hooks / lib → api → types`. Only
  `App.tsx` imports pages (exception: `RestaurantDetailsView` imports `RestaurantMenuView`,
  which belongs in `components/`, F28).

## Conventions

- `App.tsx` only maps URLs to pages and layouts. Page content lives in `pages/`.
- Not yet true: `App.tsx` holds inline JSX for the management page and the 404
  page; routing lives in `App.tsx`, not `routes/`; `routes/CustomerRouter.ts` is an unused
  `fetch` (F15, F28).
- Proposed: this folder becomes `app/` (App,
  routes, providers), `features/<feature>/`, and `shared/`, with nested layout routes, a
  central `paths` helper, and role guards.
