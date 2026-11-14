# frontend

## Purpose

The ByteBites web client: a React + TypeScript single-page app that shows restaurants and
menus and calls the FastAPI backend for all data.

## Contents

| Path | Role |
|---|---|
| `index.html` | Page shell; loads `src/index.tsx` |
| `src/` | All app code (see `src/README.md`) |
| `package.json` | Scripts and dependencies. Let npm manage `package-lock.json`; never edit it by hand |
| `tsconfig.json` | TypeScript settings (`strict`) |
| `dist/` | Build output from Parcel (git-ignored) |

Stack: React 19, React Router 7, TypeScript, Parcel (dev server and bundler), Vitest.

## How it connects

- Talks to the backend at `http://127.0.0.1:8000` through `src/api/`. The backend allows
  this origin through CORS in `main.py` (port 1234).
- `src/types/` mirrors the backend Pydantic models by hand, so the two change together.
- Run (backend running separately from the repo root):
  - `npm install`, then `npm start` → http://localhost:1234
  - `npm test` runs Vitest; `npm run build` builds to `dist/`

## Conventions

- Layering: `pages → hooks → api`. Only `src/api/` calls `fetch`; components only render.
- `.tsx` for files with JSX, `.ts` for everything else.
- Naming: PascalCase for components and their files (`RestaurantCard.tsx`) and for types;
  camelCase for functions, variables, hooks (`useDebounce.ts`), and non-component files
  (`restaurants.ts`).
- Tests sit next to the code in a `tests/` folder, named `<file>.test.ts`.
- TypeScript types disappear at runtime. The backend is the real validation; the frontend
  only shapes and displays data.
- Manual test steps for a feature go in its PR description, not here.
- Not yet true:
  - TypeScript is not installed, so nothing type-checks the code; Parcel and Vitest strip
    types without checking them (F29).
  - No linter, and CI never runs frontend tests, builds, or checks, so the architecture
    rules here are not enforced by any tool (F34).
  - The backend URL is hardcoded in several files, and `routes/CustomerRouter.ts` calls
    `fetch` outside `api/` (F15).
  - Pages fetch data in `useEffect` themselves instead of through hooks, and `api/` builds
    user-facing error text.
  - Unused code: `RestaurantCard`, `CustomerRouter.ts`, the `express` dependencies (F28).
  - Some names break the conventions above (`layouts/generic_layout/`, `test_*.test.ts`).
- Proposed:
  - Feature-first folders: `app/`, `features/<feature>/` (each page in its own folder with
    its components and hooks), and `shared/`.
  - Layout routes with role guards and a central `paths` helper.
  - Frontend types generated from the backend's OpenAPI schema.
  - Localization: `t()` catalogues, backend error codes, and `Intl` formatting in one place.
