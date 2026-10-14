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
- Artifact: backend/app/models/menu_Item_model.py
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
