# pages

## Purpose

Top-level views: one per route. A page reads the URL, gets its data through hooks or
`api/`, and arranges components. Reusable pieces belong in `components/`.

## Contents

| File | Export | Route | Shows |
|---|---|---|---|
| `LandingView.tsx` | `Landing` | `/` | Links to discover and manage restaurants |
| `DiscoverView.tsx` | `Discover` | `/restaurants` | Cuisine filter (server-side), debounced name search (client-side), restaurant list |
| `RestaurantDetailsView.tsx` | `RestaurantDetails` | `/restaurants/:restaurantId` (via a wrapper in `App.tsx` that reads the param) | Restaurant fields, then its menu |
| `RestaurantMenuView.tsx` | `RestaurantMenu` | none: rendered inside the details page | Menu items, prices, availability, retry on failure |

The management page (`/manage/restaurants`) and 404 are inline JSX in `App.tsx`.

## How it connects

- `App.tsx` maps each route to a page; `GenericLayout` wraps them all.
- Pages use `api/`, `hooks/`, `lib/`, `components/`, and `types/`. Nothing but `App.tsx`
  imports a page.
- Every page shows explicit loading (`role="status"`), error (`role="alert"`), and empty
  states.

## Conventions

- One page per route, named `<Name>Page.tsx` and exporting `<Name>Page`.
- A page with private pieces gets its own folder: `DiscoverPage/` holds the page, its
  `.module.css`, its hooks and logic, and `components/` for pieces only it uses. A page
  with none stays one file.
- Pages render; data loading lives in hooks.
- Pages read their own URL params with `useParams`.
- Not yet true:
  - `DiscoverView` shows "No restaurants available." while loading and on error, and never
    when a filter returns nothing (F35).
  - Files are `*View.tsx` and exports drop the suffix (`Discover`), so names don't match.
  - Each page fetches in its own `useEffect` (F31); `DiscoverView` builds the cuisine
    options itself.
  - `RestaurantMenuView` is a section, not a page (F28); the management page and 404 live
    in `App.tsx`.
- Proposed: data from TanStack Query hooks,
  folder-per-page colocation, and after the feature-first move, pages live in
  `features/<feature>/pages/`.
