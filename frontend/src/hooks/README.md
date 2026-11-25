# hooks

## Purpose

Reusable React hooks: stateful logic (state, effects, timers, data loading) that more than
one component or page can share, kept out of the JSX.

## Contents

| File | Hook | Used by |
|---|---|---|
| `useDebounce.ts` | `useDebounce(value, delayMs = 250)`: returns `value` only after it stops changing for `delayMs` | `DiscoverView` (name search) |
| `useCurrentAccount.ts` | `useCurrentAccount()`: asks `GET /auth/me` who the saved token belongs to. Returns `loading`, `signed-in` (with the account), `signed-out` (no token, or the backend rejected it, which also forgets it), or `error` (backend unreachable) | `RequireSignIn` |
| `useMyProfile.ts` | `useMyProfile()`: loads `GET /customers/me`. Returns `state` (`loading`, `loaded` with the profile, `not-a-customer` on 403, `error`) and `setProfile` so the page shows saved changes without reloading | `ProfileView` |
| `tests/test_useDebounce.test.ts` | Vitest + `renderHook` with fake timers | |

## How it connects

- Pages and components call hooks; hooks call `api/` and `lib/`, never `fetch` directly.
- Hooks return plain values and callbacks. They render nothing.

## Conventions

- One hook per file, named `use<Thing>.ts`, exporting a function of the same name.
- Clean up every effect (timers, subscriptions, requests) in the effect's return function.
- Test with `renderHook` from Testing Library, in `tests/<hook>.test.ts` with
  `// @vitest-environment jsdom`. Use fake timers for anything time-based.
- Not yet true:
  - Three pages repeat the same load / error / cancel logic in `useEffect`, cancelling in two
    different ways (F31).
  - The test file has a `test_` prefix (F27).
- Proposed: data hooks (`useRestaurants`,
  `useRestaurant`, `useMenu`) built on TanStack Query's `useQuery` / `useMutation`, so pages
  only render. After a feature-first move, feature-specific hooks move into their feature folder; this
  folder keeps only generic ones like `useDebounce`.
