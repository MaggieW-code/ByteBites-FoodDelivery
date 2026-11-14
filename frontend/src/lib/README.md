# lib

## Purpose

Plain TypeScript functions: data in, data out. No React, no `fetch`, no side effects, so
they are trivial to test and reuse.

## Contents

| File | Function | Used by |
|---|---|---|
| `searchRestaurants.ts` | `searchRestaurants(restaurants, query)`: restaurants whose name contains the query, case-insensitive; a blank query returns all | `DiscoverView` (client-side name search, no backend request) |
| `tests/test_searchRestaurants.test.ts` | 8 Vitest cases | |

## How it connects

- Called by pages, components, and hooks. Uses only `types/`.
- Filtering here runs on data already loaded from `api/`; server-side filters (like
  `?cuisine=`) stay in `api/`.

## Conventions

- Pure functions: same input, same output; never mutate the input array.
- One main export per file, named after the file (camelCase).
- Every function has tests in `tests/<file>.test.ts`.
- Not yet true: single-letter names (`q`, `r`) and `==` in
  `searchRestaurants.ts`; the test file has a `test_` prefix (F27); cuisine-option building
  lives inside `DiscoverView` instead of here (F31).
- Proposed: `getCuisineOptions.ts` and `format.ts` for `Intl` number, price, and
  date formatting with the current locale. After a feature-first move, feature-specific
  functions move into their feature; `shared/lib/` keeps generic ones.
