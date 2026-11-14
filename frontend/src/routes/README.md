# routes

## Purpose

URL-to-page routing: which page and layout render for each path, and who may see them.

## Contents

| File | Role |
|---|---|
| `CustomerRouter.ts` | Unused. Despite the name it holds a `fetch` call, not routes (F15, F28) |

The real routes live in `App.tsx` today: `/`, `/restaurants`, `/restaurants/:restaurantId`,
`/manage/restaurants`, and a `*` 404.

## How it connects

- `App.tsx` renders `BrowserRouter` and `<Routes>`, wrapping every route in `GenericLayout`.
- Pages link to each other with `Link` / `NavLink` and hardcoded path strings.

## Conventions

- Only routing here: paths, layouts, guards. No data fetching, no page content.
- Not yet true: routing lives in `App.tsx`, path strings are hardcoded in pages,
  one layout wraps everything, there are no role guards, and `CustomerRouter.ts` is dead code.
- Proposed:
  - A route-object tree (`createBrowserRouter`): `RootLayout` → `CustomerLayout` /
    `AdminLayout` → pages, with `RequireRole` guard routes for the Auth epic.
  - One `paths` helper (`paths.restaurant(id)`) instead of hardcoded strings.
  - Each feature exports its own routes; the app routes file only composes them, so it
    doesn't grow into one file everyone edits. Pages load with `lazy`.
  - At most three levels: Root → audience layout → page.
