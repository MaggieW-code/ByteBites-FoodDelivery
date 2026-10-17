# AI Provenance

This file records how generative AI was used to produce or influence artifacts in this project,
following the course's Generative AI Use and Provenance Guide.

Labels: `AI-GENERATED`, `AI-ASSISTED`, `AI-REVISED`, `NO-AI`

## Entries

### Entry 1

- Student(s): Junho Kim
- Artifact: backend/app/data/menu_items.json
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Create representative menu item persistence data for the Add Menu Item user story (#70).
- Influence: Started from one sample entry written by the student. The AI generated the remaining
  sample items (10 total across rest_001–rest_005), renamed the `rest_id` key to `restaurant_id`
  to match the `MenuItem` model, and changed the category values to menu sections
  (Mains, Sides, Drinks, Desserts).
- Validation: Loaded every item through the `MenuItem` Pydantic model and checked that each
  `restaurant_id` exists in `backend/app/data/restaurants.json`.
- PR: TBD

### Entry 2

- Student(s): Junho Kim
- Artifact: backend/app/models/menu_item_model.py
- Label: AI-ASSISTED
- AI tool: Claude (Claude Code)
- Purpose: Understand how to design the menu item Pydantic model for the Add Menu Item user story (#70).
- Influence: Adopted the suggested split into `CreateMenuItem` (request body sent by the user) and
  `MenuItem` (stored item, extends `CreateMenuItem` and adds `id` and `restaurant_id`). Fields and
  validation rules were written by the student following the existing `restaurant_model.py` format.
- Validation: Checked that invalid input (string price, price of 0, empty name, wrong-length id,
  non-boolean `is_available`) is rejected and that all sample data in `menu_items.json` loads
  through the model.
- PR: TBD

### Entry 3

- Student(s): Junho Kim
- Artifact: backend/app/services/menu_service.py
- Label: AI-ASSISTED
- AI tool: Claude (Claude Code)
- Purpose: Understand and implement the service layer for the Add Menu Item user story (#70).
- Influence: The AI explained list comprehensions and `**` dict unpacking in the existing
  `restaurant_service.py`, and suggested the structure of `add_menu`: take a `CreateMenuItem`
  and a `restaurant_id`, generate an 8-character id with `uuid`, build the full `MenuItem`,
  save it through the repository and return it. The AI also reviewed the student's drafts and
  pointed out bugs (wrong return type on `get_menu`, `repository.append` instead of `add`,
  `data` typed as `MenuItem` instead of `CreateMenuItem`, missing import). The student typed
  the code and made the fixes.
- Validation: Ran `add_menu` and `get_menu` against a temporary JSON file and confirmed the new
  item was saved with a generated id; covered by `backend/tests/test_menu_service.py`.
- PR: TBD

### Entry 4

- Student(s): Junho Kim
- Artifact: backend/app/routes/menu_routes.py, main.py
- Label: AI-ASSISTED
- AI tool: Claude (Claude Code)
- Purpose: Expose adding a menu item as an API endpoint for the Add Menu Item user story (#70).
- Influence: The AI suggested the `POST /restaurants/{restaurant_id}/menu` route following the
  existing `restaurant_routes.py` format, explained it line by line, and gave the two lines to
  register the router in `main.py`. The student typed the code.
- Validation: Confirmed the endpoint returns 201 with a generated id for a valid request and 422
  for a missing field, and that the route is registered in the app; covered by
  `backend/tests/test_menu_routes.py`.
- PR: TBD

### Entry 5

- Student(s): Junho Kim
- Artifact: backend/tests/test_menu_item_model.py, backend/tests/test_menu_repository.py,
  backend/tests/test_menu_service.py, backend/tests/test_menu_routes.py
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Test the model, repository, service and route for the Add Menu Item user story (#70).
- Influence: The AI wrote all four test files (28 tests), following the format of the existing
  restaurant test files. The route tests use a small app containing only the menu router.
- Validation: Ran the full test suite (55 passed, including the existing tests) and checked that
  the tests use temporary files and do not modify the real data files.
- PR: TBD

### Entry 6

- Student(s): Junho Kim
- Artifact: backend/app/models/update_menu_item_model.py
- Label: AI-ASSISTED
- AI tool: Claude (Claude Code)
- Purpose: Define the request model for the Update Menu Item user story (#76).
- Influence: The AI explained why an update needs its own model with all fields optional (so the
  owner can send only the fields that change), and explained `str | None`, `default = None` and
  `gt` vs `ge`. The student wrote the model by copying `CreateMenuItem` and making each field
  optional, then fixed the issues the AI pointed out in review (a missing comma, a `0.0` price
  default instead of `None`, and an accidentally copied `MenuItem` class).
- Validation: Checked that partial updates are accepted and that invalid values (empty name or
  category, zero or negative price, wrong types) are rejected; covered by
  `backend/tests/test_update_menu_item_model.py`.
- PR: TBD

### Entry 7

- Student(s): Junho Kim
- Artifact: backend/app/repositories/menu_repository.py (`update` method)
- Label: AI-ASSISTED
- AI tool: Claude (Claude Code)
- Purpose: Persist menu item updates for the Update Menu Item user story (#76).
- Influence: The AI suggested basing `update` on the existing `add` method and provided the
  `enumerate` loop that finds the item with the matching id and replaces it, and explained how it
  works. The student wrote the method.
- Validation: Ran `update` against a temporary JSON file and confirmed only the matching item
  changed; covered by `backend/tests/test_menu_repository.py`.
- PR: TBD

### Entry 8

- Student(s): Junho Kim
- Artifact: backend/app/services/menu_service.py (`update_menu` method, `MenuItemNotFoundError`)
- Label: AI-ASSISTED
- AI tool: Claude (Claude Code)
- Purpose: Implement the update business logic for the Update Menu Item user story (#76).
- Influence: The AI proposed the design (find the item matching both the menu item id and the
  restaurant id, apply only the fields that were sent, save, return it, and raise
  `MenuItemNotFoundError` otherwise), explained it as plain-English steps, and provided the code
  for each step, including `model_dump(exclude_none=True)` and `model_copy(update=...)`. The
  student typed the code.
- Validation: Ran the service against a temporary JSON file and confirmed price-only updates,
  unknown items and wrong restaurants behave correctly; covered by
  `backend/tests/test_menu_service.py`.
- PR: TBD

### Entry 9

- Student(s): Junho Kim
- Artifact: backend/app/routes/menu_routes.py (`PATCH /restaurants/{restaurant_id}/menu/{menu_item_id}`)
- Label: AI-ASSISTED
- AI tool: Claude (Claude Code)
- Purpose: Expose updating a menu item as an API endpoint for the Update Menu Item user story (#76).
- Influence: The AI provided the route code, including the try/except that turns
  `MenuItemNotFoundError` into a 404, and explained the parameters and status codes. The student
  typed the code and fixed the issues the AI pointed out in review (missing `{menu_item_id}` in
  the URL, missing imports, duplicate imports).
- Validation: Confirmed the endpoint returns 200 for a valid update, 404 for an unknown item or
  wrong restaurant, and 422 for an invalid price; covered by `backend/tests/test_menu_routes.py`.
- PR: TBD

### Entry 10

- Student(s): Junho Kim
- Artifact: backend/tests/test_update_menu_item_model.py, and the update tests added to
  backend/tests/test_menu_repository.py, backend/tests/test_menu_service.py,
  backend/tests/test_menu_routes.py
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Test the model, repository, service and route for the Update Menu Item user story (#76).
- Influence: The AI wrote all 22 update tests, following the format of the existing menu test
  files, and mapped them to the acceptance criteria of #76.
- Validation: Ran the full test suite (77 passed, including the existing tests) and checked that
  the tests use temporary files and do not modify the real data files.
- PR: TBD

### Entry 11

- Student(s): Yibing Wang
- Artifact: frontend/src/pages/LandingView.tsx, frontend/src/App.tsx,
  frontend/src/layouts/generic_layout/GenericLayout.tsx,
  frontend/src/pages/DiscoverView.tsx, frontend/src/pages/RestaurantDetailsView.tsx,
  frontend/src/api/restaurants.ts
- Label: AI-ASSISTED
- AI tool: OpenAI Codex
- Purpose: Add a landing page separating restaurant discovery from the future
  restaurant-management section, with URL-based navigation.
- Influence: Codex generated the landing page and routing changes, moved restaurant
  API calls from CustomerRouter.ts into api/restaurants.ts, and updated imports.
  The student edited and the scope with simpler text and Home-only header
  navigation. Management remains a placeholder.
- Validation: Codex ran the frontend production build successfully and the backend
  test suite (40 passed at the time). Browser interactions were not verified.
- PR: 100

### Entry 12

- Student(s): Maison Gulyas
- Artifact: frontend/src/App.tsx, frontend/src/index.tsx, frontend/src/routes/CustomerRouter.ts,
  frontend/src/layouts/generic_layout/GenericLayout.tsx, frontend/src/pages/DiscoverView.tsx,
  frontend/src/components/RestaurantCard.tsx, frontend/src/types/, frontend/README.md
- Label: AI-ASSISTED
- AI tool: Claude (Claude Code)
- Purpose: I set up the frontend architecture (pages, layouts, components, routes, types) for the
  Restaurant List View subtask (#29) so the team has a consistent structure for future UI work.
- Influence: Claude generated the initial folder structure and file scaffolding, and I used it to
  discuss architecture options. I reworked the structure, wrote the page, layout and component
  content, and used Claude to check my understanding of the design choices.
- Validation: I ran the frontend locally and confirmed the restaurant list loaded from the backend
  through the Discover page.
- PR: 91

### Entry 13

- Student(s): Maison Gulyas
- Artifact: frontend/src/hooks/useDebounce.ts, frontend/src/hooks/tests/test_useDebounce.test.ts,
  frontend/src/lib/searchRestaurants.ts, frontend/src/lib/tests/test_searchRestaurants.test.ts,
  frontend/src/pages/DiscoverView.tsx, frontend/package.json
- Label: AI-ASSISTED
- AI tool: Claude (Claude Code)
- Purpose: I wanted to learn how to write a custom React hook and a search utility for the Search
  and Filter Restaurants user story (#36), since I hadn't written either before.
- Influence: Claude provided scaffolding for the hook and search function and explained how
  debouncing works. I changed the code as needed and used Claude to check my understanding.
  Claude also helped me weigh short-term vs. scalable options (a simple client-side search now
  vs. server-side search or a Trie later); I chose the simple approach for now.
- Validation: I ran `npm run test` (vitest) and all 13 hook and search tests passed.
- PR: 109

### Entry 14

- Student(s): Yibing Wang
- Artifact: backend/app/services/restaurant_service.py,
  backend/app/routes/restaurant_routes.py, frontend/src/api/restaurants.ts,
  frontend/src/pages/DiscoverView.tsx, backend/tests/test_restaurant_cuisine_filter.py
- Label: AI-GENERATED
- AI tool: OpenAI Codex
- Purpose: Implement filtering restaurants by cuisine for user story #36.
- Influence: The student requested cuisine filtering. Codex generated an optional
  cuisine query parameter, service-layer filtering using repository-loaded data,
  and a frontend dropdown populated from API results. Matching ignores case and
  surrounding whitespace; an empty filter returns all restaurants. Codex also
  generated isolated service and API tests for matching, no matches, and the
  unfiltered list.
- Validation: Ran the full pytest suite (111 passed) and the frontend production
  build successfully. Filter tests use temporary JSON files. Browser interactions
  were not verified.
- PR: TBD

### Entry 15

- Student(s): Junho Kim
- Artifact: README.md, docs/architecture.md, docs/scrum.md
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Update the project documentation to reflect the Milestone 1 implementation.
- Influence: The AI read the routes, models and git history and wrote the README sections
  (current status, frontend setup, endpoint list with request fields and error codes,
  repository structure), the feature layer mapping and frontend structure in
  `architecture.md`, and the Milestone 1 meeting notes, progress log, decisions and blockers
  in `scrum.md`. The student provided the weekly Friday meeting schedule and team member names,
  and corrected a name spelling.
- Validation: Checked the endpoint descriptions against `restaurant_routes.py` and
  `menu_routes.py`, ran the test suite (100 passed). The meeting notes were inferred by the AI
  from commit dates and were reviewed by the student.
- PR: 108
