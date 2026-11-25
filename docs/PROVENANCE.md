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

### Entry 16

- Student(s): Maison Gulyas
- Artifact: `AGENTS.md`, `CLAUDE.md`, `.claude/skills/` (`review-pr`, `lint`, `study`,
  `fix-finding`, `audit-security`, `audit-hooks`), `docs/agent_usage.md`, `.gitignore`, `.githooks/pre-commit`, `ruff.toml`,
  `requirements.txt`, `.github/workflows/python-app.yml`, `frontend/README.md`, and a
  `README.md` in every major backend, frontend, and docs folder
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Set up an agentic workflow and document every folder before commencing work on the repo.
- Influence: I set the rules, structure, and decisions; the AI drafted the files. The AI
  also reviewed each folder and reported issues, which I logged for later fix PRs.
  Replaced flake8 with ruff (same checks, line length kept at 127).
- Validation: I reviewed and approved each README one at a time and checked them against
  the code. Backend tests (111) and frontend tests (13) pass; no app code changed.
- PR: #125 

### Entry 17

- Student(s): Maison Gulyas
- Artifact: `frontend/src/pages/DiscoverView.tsx`, `frontend/src/pages/tests/DiscoverView.test.tsx` (new),
  `frontend/src/pages/README.md`, `backend/tests/test_restaurant_routes.py`, `backend/tests/README.md`
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Fix the inverted empty-state message on Discover and add tests. Update the backend test to use temporary data. Likewise, found the backend bug which was touching actual data and adapted that with Claude. 
- Influence: I found the bug earlier and had Claude implement the fix with new tests.
- Validation: I checked the tests by making the fix un-true and re-running them as well as visually validating the change. 
- PR: #129 

### Entry 18

- Student(s): Maison Gulyas
- Artifact: `backend/tests/conftest.py`, `backend/tests/test_menu_routes.py`,
  `backend/tests/test_restaurant_management.py`, `backend/tests/test_restaurant_routes.py`,
  `backend/tests/test_menu.py`, `backend/tests/test_restaurant_details.py`,
  `backend/tests/test_restaurant_cuisine_filter.py`, `backend/tests/test_config.py`,
  `backend/tests/test_health_routes.py`, `backend/tests/README.md`
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Each test module built its own data and paths, which made tests brittle and let them
  drift out of date. Move shared test data and clients into `conftest.py` fixtures so every test
  uses one source of truth.
- Influence: I learned the shared-fixture pattern, reviewed our tests, and decided it fit. Claude
  did most of the refactor; I reviewed and adjusted the changes.
- Validation: Ran the full backend suite before and after the refactor: 111 passed both times, so
  no tests were lost.
- PR: #146

### Entry 19

- Student(s): Maison Gulyas
- Artifact: `backend/app/models/account_model.py` (new), `backend/app/models/auth_model.py` (new),
  `backend/tests/auth/test_account_model.py` (new), `backend/tests/auth/test_auth_model.py` (new),
  `backend/app/models/README.md`, `backend/tests/README.md`, `backend/tests/auth/README.md` (new)
- Label: AI-ASSISTED
- AI tool: Claude (Claude Code)
- Purpose: Help speedup writing models and tests. Models were implemented by me and polished by Claude.  
- Influence: Models and aliases. 
- Validation: Had tests written, broke models and fixed them, then finally updated models. 
- PR: #147

### Entry 20

- Student(s): Maison Gulyas
- Artifact: `backend/app/repositories/json_list_store.py` (new),
  `backend/app/repositories/account_repository.py` (new),
  `backend/app/repositories/session_repository.py` (new), `backend/tests/auth/conftest.py` (new),
  `backend/tests/auth/test_account_repository.py` (new),
  `backend/tests/auth/test_session_repository.py` (new), `backend/tests/test_json_list_store.py` (new),
  `backend/app/repositories/README.md`, `backend/tests/README.md`, `backend/tests/auth/README.md`
- Label: AI-ASSISTED
- AI tool: Claude (Claude Code)
- Purpose: Assistance instantiating the authentication Repository layer.
- Influence: My agent updated README's and tests, I gave it the architecture I wanted it to follow and what I needed done. The major assist was on the `architecture change` with `json_list_store.py` where an issue with the current data storage system was found. By using `atomic writes` we can safely update files. Essentially a new copy is written and then swapped with the old copy. Upon success the new copy is the now current copy, otherwise the old copy remains the current.  
- Validation: Ran tests, confirmed logic. All tests passed.
- PR: #148

### Entry 21

- Student(s): Maison Gulyas
- Artifact: `backend/app/services/auth_service.py` (new), `backend/app/services/password_hashing.py` (new),
  `backend/app/dependencies/auth.py` (new), `backend/app/dependencies/__init__.py` (new),
  `backend/app/dependencies/README.md` (new), `backend/app/config.py`, `backend/app/models/auth_model.py`
  (`TokenResponse`), `backend/tests/auth/test_auth_service.py` (new),
  `backend/tests/auth/test_password_hashing.py` (new), `backend/tests/auth/test_auth_dependencies.py` (new),
  `backend/tests/auth/test_auth_config.py` (new), `backend/tests/auth/auth_helpers.py` (new),
  `backend/tests/auth/conftest.py`, `backend/tests/auth/test_auth_model.py`,
  `backend/tests/auth/test_account_repository.py`, `backend/app/README.md`, `backend/app/services/README.md`,
  `backend/app/models/README.md`, `backend/tests/auth/README.md`
- Label: AI-ASSISTED
- AI tool: Claude (Claude Code)
- Purpose: Essentially pair-coded. Went through different situations and pivoted as needed. 
- Influence: The major influence was the dependency directory, it was a thought I had toyed with before however Claude gave concrete evidence for implementing it and checking industry standard. That being said the main intention is quick implementationa due to due dates and then refactorization after handing in M2. 
- Validation: Checked tests, had it teach implementations back to me I didn't understand. 
- PR: #149

### Entry 22

- Student(s): Maison Gulyas
- Artifact: `backend/app/routes/auth_routes.py` (new), `backend/tests/auth/test_auth_routes.py` (new),
  `backend/app/data/accounts.json` (new), `main.py`, `.gitignore`, `backend/tests/auth/conftest.py`,
  `backend/app/routes/README.md`, `backend/app/data/README.md`, `backend/tests/README.md`,
  `backend/tests/auth/README.md`, `docs/architecture.md`
- Label:  AI-ASSISTED 
- AI tool: Claude (Claude Code)
- Purpose: Due to the fast pace that needs to occur to get this assignment done at this moment I had Claude co-code with me to get it done and walk me through changes as I implemented them and asked questions.
- Influence: Tests and Routes since we had a error in a our structure with previous routes that will still need to be refactored that tend to break our architecture. 
- Validation: Running tests, buidling the application and testing sign-in and signout as well as /me endpoints.
- PR: #150

### Entry 23

- Student(s): Junho Kim
- Artifact: backend/app/routes/menu_routes.py, backend/tests/test_menu_routes.py
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Return 422 for a badly formatted restaurant ID when adding a menu item (#123).
- Influence: The AI added the same 8-character `PathParameter` rule used by the GET menu route
  to the POST route, and wrote route tests for 201 (existing restaurant) and 422
  (`rest_01`, `rest_0001`, `r`, with nothing saved). The student reviewed the change and
  explained back how FastAPI rejects the request before the service runs.
- Validation: Ran the full pytest suite (118 passed). Confirmed the new 422 tests fail when
  the route change is removed.
- PR: 132

### Entry 24

- Student(s): Junho Kim
- Artifact: backend/app/repositories/menu_repository.py, backend/app/services/menu_service.py
- Label: AI-ASSISTED
- AI tool: Claude (Claude Code)
- Purpose: Add menu item lookup by ID for Cart and Checkout (#124).
- Influence: The AI explained the route → service → repository structure, gave a worked
  example of a nested-loop search on sample data, and reviewed the student's code. The student
  wrote `find_item_by_id` and `get_menu_item`, fixing issues found in review (missing
  `get_all()` call, `return None` inside the loop, wrong repository method, missing return).
  After checking the Cart (#117) and Checkout (#118) requirements, the student decided to also
  check that the item's restaurant exists and is active; the AI provided the structure for that
  check and the new `MenuRestaurantInactiveError`, which the student typed in.
- Validation: Called `get_menu_item` on every item in `menus.json` and an unknown ID; ran the
  full pytest suite.
- PR: 132

### Entry 25

- Student(s): Junho Kim
- Artifact: backend/tests/test_menu_service.py
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Test the menu item lookup for #124.
- Influence: The AI wrote four service tests: item found (price, availability, restaurant ID),
  unknown item, inactive restaurant, and missing restaurant.
- Validation: Ran the full pytest suite (122 passed). Confirmed the inactive-restaurant test
  fails when the `is_active` check is removed.
- PR: 132

### Entry 26

- Student(s): Junho Kim
- Artifact: README.md, backend/README.md
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Document the Restaurant & Menu Integration epic (#116).
- Influence: The AI added the 404/422 rules for adding a menu item, the decimal price format,
  and the `get_menu_item` lookup and its errors.
- Validation: Checked the descriptions against `menu_routes.py` and `menu_service.py`.
- PR: 132

### Entry 27

- Student(s): Junho Kim
- Artifact: backend/app/models/menu_model.py, backend/app/repositories/menu_repository.py,
  backend/app/services/menu_service.py, backend/app/validation_errors.py, main.py,
  backend/tests/test_menu_routes.py, backend/tests/test_menu_repository.py,
  backend/tests/test_menu_service.py, backend/tests/test_menu_item_model.py,
  backend/tests/test_update_menu_item_model.py, README.md, backend/README.md
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Address PR #132 review comments on the price format and global menu item ID lookup.
- Influence: The AI defined the price rule (number or decimal string, 0 or more so free items
  work with Checkout #144, at most 2 decimal places, at most 999999.99, no inf/nan) with Pydantic `Field` constraints, added a
  422 handler so rejected inputs like `1e999` no longer cause a 500, made new item IDs unique
  across all menus, made `find_item_by_id` raise `DuplicateMenuItemIdError` on duplicate IDs,
  and wrote route, repository and service tests for these cases. The student asked for the fix
  because of the deadline and reviewed the changes. The team decided to allow a price of 0.
  After rebasing on main, the AI resolved the provenance conflict (renumbered entries after
  Entry 16), updated the folder READMEs in `backend/app/models`, `services` and `data` that
  still described the old menu model files, and fixed ruff warnings in the files this PR touches.
  After merging main (#146), the AI resolved the conflicts in `backend/tests/test_menu_routes.py`
  by moving this PR's menu route tests onto the shared `client` and `menus_file` fixtures in
  `conftest.py`, kept the invalid price test at -1 because 0 is now a valid price, and renumbered
  this PR's provenance entries to 23-27 after Entries 17-22 from main.
- Validation: Ran the full pytest suite (151 passed) before and after the merge. Confirmed the new
  tests fail when each fix is removed.
- PR: 132

### Entry 28

- Student(s): Junho Kim
- Artifact: backend/app/services/menu_service.py, backend/tests/test_menu_service.py,
  backend/app/README.md, backend/README.md, README.md
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Address Maison's second review on #132: document `validation_errors.py`, stop the
  repository's `DuplicateMenuItemIdError` leaking out of `MenuService`, and replace the two merge
  commits with a linear history so the epic can be merged with Rebase and merge.
- Influence: The AI added `MenuDataIntegrityError` and made `get_menu_item` raise it instead of
  the repository error, wrote a service test for the duplicate ID case, added
  `validation_errors.py` to the `backend/app` README and updated the error lists in both
  READMEs. The AI gave the git commands to squash the branch onto `origin/main`; the student ran
  them.
- Validation: Ran the full pytest suite (260 passed). Confirmed the new test fails when the error
  wrapping is removed. Checked that the squashed commit has the same content as the old branch head.
- PR: 132

### Entry 29

- Student(s): Junho Kim
- Artifact: backend/app/models/restaurant_model.py, backend/app/models/menu_model.py,
  backend/app/routes/menu_routes.py, backend/app/routes/restaurant_routes.py,
  backend/tests/test_menu_routes.py, backend/app/models/README.md, backend/app/routes/README.md,
  README.md, backend/README.md
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Address Maison's suggestion on #132 to define the 8-character ID rule once and to
  validate IDs on the PATCH menu route.
- Influence: The AI defined `RestaurantId` in `restaurant_model.py` and `MenuItemId` in
  `menu_model.py`, used them in the models and in the GET/POST/PATCH menu routes and the GET
  restaurant route, and wrote PATCH and GET menu route tests for bad ID lengths (GET menu had
  none, so switching it to the wrong form would have gone unnoticed). The AI tested both ways of
  attaching `Path(...)` and found that `x: RestaurantId = Path(...)` silently drops the rule, so
  the routes use `Annotated[RestaurantId, Path(...)]` and the routes README warns about it.
  `EightCharId` in `account_model.py` was left alone because it is the account ID rule.
- Validation: Ran the full pytest suite (267 passed). Confirmed the new PATCH test fails when the
  route goes back to plain `str` parameters and the GET menu test fails with `= Path(...)`. No new ruff warnings in the changed files.
- PR: 132

### Entry 30

- Student(s): Junho Kim
- Artifact: backend/app/routes/menu_routes.py, backend/tests/test_menu_routes.py,
  backend/app/routes/README.md
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Handle `MenuReadError` from #140 in the GET menu route so unreadable menu data
  returns a clear 500 instead of an unexplained one.
- Influence: The AI added the `MenuReadError` handler and the 500 entry in `responses`, wrote a
  regression test with three kinds of broken menu data, and updated the routes README.
- Validation: Ran the full pytest suite (380 passed). Confirmed the new test fails without the
  handler. No new ruff warnings in the changed files.
- PR: 155

### Entry 31

- Student(s):
- Artifact: 
  backend/app/repositories/accounts/session_repository.py (moved),
  backend/app/services/accounts/account_factory.py (new),
  backend/app/services/accounts/account_service.py (new),
  backend/app/services/accounts/auth_service.py (moved),
  backend/app/services/accounts/password_hashing.py (moved),
  backend/app/routes/accounts/customer_routes.py (new), 
  backend/app/routes/accounts/auth_routes.py (moved),
  backend/app/dependencies/auth.py, 
  main.py,
  backend/tests/auth/*, 
  AGENTS.md,
  */README.md
- Label: AI-ASSISTED | AI-REVISED
- AI tool: Claude (Claude Code)
- Purpose: I prompted Claude to assist with developing. All pivitol decisions and architecture changes were mine. I used it to help 
  implement the backend logic for accounts at an accelerated rate. Furthermore, I had Claude handle testing for me. 
- Influence: Tests, and basic logic imlementation, however refrained from leting Claude dictate architecture, and actually caught some bugs or 'mistakes' 
  it would try implementing here or there.
- Validation: Manually ran tests in `uvicorn main:app` and pytest.
- PR: #156

### Entry 32

- Student(s):
- Artifact: frontend/src/api/client.ts (new), frontend/src/api/accounts.ts (new),
  frontend/src/types/account.ts (new), frontend/src/hooks/useCurrentAccount.ts (new),
  frontend/src/hooks/useMyProfile.ts (new), frontend/src/routes/RequireSignIn.tsx (new),
  frontend/src/pages/AccountView.tsx (new), frontend/src/pages/ProfileView.tsx (new),
  frontend/src/App.tsx, frontend/src/layouts/generic_layout/GenericLayout.tsx,
  frontend/src/api/tests/*, frontend/src/pages/tests/*, frontend/src/routes/tests/*,
  frontend/src/layouts/generic_layout/tests/*, frontend/src/*/README.md, frontend/src/README.md
- Label: AI-GENERATED
- AI tool: Claude (Claude Code)
- Purpose: Needed to implement the frontend without enough time to fully do it myself. I have personal documentation on refactors, architecture, ruling, and finding's I want to implement as time goes on so I had it go through that for reference.
- Validation: I tested everything manually and in repo and browser.
- PR: #158

### Entry 34

- Student(s):
- Artifact: backend/app/services/checkout_service.py (new), backend/app/services/cart_service.py,
  backend/app/models/checkout_model.py (new), backend/app/models/cart_model.py,
  backend/app/repositories/cart_repository.py, backend/app/routes/checkout_routes.py (new),
  backend/app/routes/cart_routes.py, backend/app/dependencies/commerce.py (new),
  backend/app/menu_dependencies.py, main.py, .gitignore, backend/tests/test_checkout_service.py (new),
  backend/tests/test_checkout_routes.py (new), backend/tests/test_order_checkout_flow.py (new),
  backend/tests/test_cart_service.py, backend/app/*/README.md, backend/tests/README.md
- Label: <!-- AI-GENERATED | AI-ASSISTED | AI-REVISED | NO-AI -->
- AI tool:
- Purpose:
- Influence:
- Validation:
- PR: 144
