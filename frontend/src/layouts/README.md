# layouts

## Purpose

The frame shared by many pages: header, navigation, and where page content goes. Pages
supply the content; layouts never fetch data or hold page logic.

## Contents

| Path | Renders | Used by |
|---|---|---|
| `generic_layout/GenericLayout.tsx` | Header with the ByteBites home link and a nav (Home), then `children` | `App.tsx`, wrapping every route |

## How it connects

- `App.tsx` wraps the whole `<Routes>` in `GenericLayout`, so every page, including 404,
  gets the same header.
- Uses `NavLink` from React Router for navigation links.

## Conventions

- Layouts nest: `RootLayout` (the app frame every page gets: brand header, language
  switcher) → one layout per audience (`CustomerLayout`, `AdminLayout`) → pages. Add a
  middle layout only when its pages share UI, and never nest deeper than these three levels.
- Each layout has its own folder named after it: `RootLayout/` holds `RootLayout.tsx`,
  `RootLayout.module.css`, and a `components/` folder for pieces only that layout uses
  (`Header`, `LanguageSwitcher`). Components shared with pages stay in `src/components/`.
- A layout renders shared chrome plus a slot for the page; nothing page-specific.
- Localization: the layout owns the language switcher and translates its own strings. The
  locale provider sits at the app root (above every layout), and each component translates
  its own text with `t()`.
- Not yet true:
  - The `generic_layout/` folder is snake_case; a single-file layout needs no folder (F27).
  - `className`s like `generic-layout_header` point at no stylesheet: the app has no CSS
    at all (F33).
  - One layout wraps every route, so customer and admin pages can't differ.
- Proposed: layouts become **layout routes** that render
  `<Outlet />`. `GenericLayout` is renamed `RootLayout` and stays the top of the tree;
  `CustomerLayout` and `AdminLayout` nest under it, with `RequireRole` guard routes for the
  Auth epic. After a feature-first move they live in `shared/layouts/`.
