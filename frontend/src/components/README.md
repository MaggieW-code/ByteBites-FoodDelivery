# components

## Purpose

Reusable UI pieces. A component renders from its props and its own local state; it can be
dropped into any page.

## Contents

| File | What it renders | Used by |
|---|---|---|
| `CreateRestaurantForm.tsx` | Name / cuisine / address form → `createRestaurant`, then shows the created restaurant | `/manage/restaurants` (inline in `App.tsx`) |
| `UpdateRestaurantForm.tsx` | Restaurant ID + optional new fields → `updateRestaurant`, then shows the result | `/manage/restaurants` |
| `RestaurantCard.tsx` | Clickable card with image, rating, wait time, delivery price | Nothing (unused, F28) |

## How it connects

- Rendered by pages (and, for now, inline JSX in `App.tsx`).
- Get data through props or hooks; may call `api/` functions for their own actions (form
  submits), never `fetch`.
- Types come from `types/`.

## Conventions

- One component per file; PascalCase file and export name (`RestaurantCard.tsx` exports
  `RestaurantCard`). Named exports, no default exports.
- A component's props type lives in the same file, not in `types/`.
- Accessible by default: every input has a `<label htmlFor>`, errors use `role="alert"`,
  status messages use `role="status"`.
- Not yet true:
  - Both forms import `type Restaurant` from `api/restaurants.ts`, which doesn't export it.
    It only runs because nothing type-checks (F29).
  - The two forms are near-copies (state, validation, submit, error handling), and the
    update form asks the user to type a raw restaurant ID (F32).
  - `RestaurantCard`'s props type lives in `types/` and matches no backend data (F16, F28).
- Proposed: forms use React Hook Form with Zod
  schemas (starting with Customer Accounts), submit through TanStack Query mutations, and
  show `ApiError` field errors; after the move, feature components live in
  `features/<feature>/components/` and only generic UI stays in `shared/ui/`.
