# Required Architectural Improvements (Milestone 2)

Each developer lists at least one architectural or design improvement, with evidence:
implementation, tests, integration, or peer review.

| Developer | Improvement(s) | Rubric category | Evidence |
|---|---|---|---|
| Maison | Shared test fixtures (conftest), account factory, account code grouping, value checks on model types, delivery address IDs | Testability, remove duplication, service responsibilities, model organisation, coupling | PR #146, commits on `mais/epic-114/customer-accounts`, #114 |
| Developer 2 |  |  |  |
| Developer 3 |  |  |  |
| Developer 4 |  |  |  |

---

## Maison

### 1. Shared test fixtures in `conftest.py`

- **Category:** improve testability; remove duplicated setup.
- **Problem:** each test file built its own data files, repositories, services and client.
  The same setup was copied across files and drifted apart.
- **Change:**
  - `backend/tests/conftest.py` is the single source of test setup. Fixtures chain:
    records → JSON file in `tmp_path` → repository → service → `client`.
  - Any test can override the data with its own `*_records` fixture or with `parametrize`.
  - One `TestClient` is shared per session. `client` points the routes at the test's
    services through `monkeypatch`, and that is undone after each test.
  - `backend/tests/auth/conftest.py` extends it for accounts:
    - account and session records
    - a `FakeClock` for expiry
    - `auth_service` and `account_service` on the same repository
    - `client` overrides both providers with `dependency_overrides`
    - an `auth_headers(email)` fixture that returns sign-in headers
    - one shared scrypt hash per session, so tests stay fast
- **Evidence:** PR #146 (`dec2987`) changed 11 files, +360 / −494 lines (net −134). Every
  account test since then (`backend/tests/auth/*`) uses these fixtures.
- **Files:** `backend/tests/conftest.py`, `backend/tests/auth/conftest.py`, `backend/tests/README.md`

### 2. Factory for new accounts (`AccountFactory`)

- **Category:** clarify service responsibilities; reduce coupling.
- **Problem:** registration mixed "is this allowed?" (email already taken) with "build the
  record" (ID, hashed password, `is_active`, class per role).
- **Change:**
  - `AccountFactory.create(request, role, account_id=...)` is the one place that defines what
    a new account looks like.
  - The class comes from the `role` value through the `StoredAccount` union. No second
    role-to-class table to keep in sync.
  - The service generates the ID and passes it in, so the factory never calls back into it.
  - The password hasher is injected, so tests use a fast fake instead of scrypt.
  - `AccountService` decides, `AccountFactory` builds, `AccountRepository` saves.
- **Evidence:** commit `0096051`; `backend/tests/auth/test_account_factory.py` (class per role,
  unknown role rejected, only the hash stored, new accounts active).
- **Files:** `backend/app/services/accounts/account_factory.py` (new),
  `backend/app/services/accounts/account_service.py`

### 3. Account code grouped by feature inside each layer

- **Category:** improve module organisation; reduce coupling.
- **Problem:** account and auth files were mixed in with restaurant and menu files in every
  layer, and `AuthService` held both sign-in and account management.
- **Change:**
  - `accounts/` subfolders in `models/`, `repositories/`, `services/` and `routes/`.
  - The layers stay the top-level folders, so the layered architecture is unchanged.
  - `AuthService` (sign-in, tokens, sign-out) and the new `AccountService` (register, profile,
    addresses, deactivate) are now separate classes.
  - The rule is in `docs/architecture.md`: a feature with several files in a layer gets a
    subfolder.
- **Evidence:** commit `0096051`. C3–C5 then added code only to `accounts/` and `AccountService`.
- **Files:** `backend/app/{models,repositories,services,routes}/accounts/*`,
  `backend/app/dependencies/auth.py`, `main.py`, `docs/architecture.md`

### 4. Value checks on model types

- **Category:** remove duplicated validation; improve Pydantic model organisation.
- **Problem:** email checks only measured length (`abc` was accepted), phones were free
  text, and passwords had no minimum length.
- **Change:** each type is defined once and reused by every model that needs it.
  - `Email` uses `EmailStr`, trimmed and lowercased. Registration and updates use it.
  - `LoginEmail` only trims and lowercases, so sign-in looks an email up without checking
    its format. An unknown or badly formed email gets the same 401.
  - `PhoneNumber` is checked by libphonenumber (Canada only) and stored as E.164
    (`+12502221234`).
  - Passwords must be 8–128 characters.
  - AGENTS.md and `architecture.md` now say:
    - checks that need only the value go on models (FastAPI returns 422);
    - checks that need stored data go in services.
- **Evidence:** commit `0096051`; model tests for invalid emails, phones and passwords. A
  seed-file test caught demo data that broke the new rules.
- **Files:** `backend/app/models/accounts/account_model.py`,
  `backend/app/models/accounts/auth_model.py`, `AGENTS.md`, `docs/architecture.md`,
  `requirements.txt`

### 5. Delivery address IDs and their own endpoints

- **Category:** design improvement found during integration.
- **Problem:** `PATCH /customers/me` replaced the whole address list. Sending only a new
  address silently deleted the others and still returned 200.
- **Change:**
  - Each `DeliveryAddress` has an 8-character `id`, unique within its customer.
  - New endpoints: `POST /customers/me/addresses`, and `PATCH` and `DELETE`
    `/customers/me/addresses/{address_id}`.
  - Addresses are always looked up through the signed-in customer, so one customer can't
    reach another's addresses (404).
  - The create request and the stored address share a `DeliveryAddressFields` base, and both
    PATCH bodies share `PartialUpdateRequest` (at least one field, no nulls).
- **Evidence:** commit `022baf0`; route tests: earlier addresses kept on add, only one address
  edited or removed, 404 for unknown and other customers' IDs, 401/403 on every route.
- **Files:** `backend/app/models/accounts/account_model.py`,
  `backend/app/services/accounts/account_service.py`,
  `backend/app/routes/accounts/customer_routes.py`, `main.py` (CORS allows `DELETE`)

**Overall evidence:** backend tests grew from 219 to 381 passing across the epic. Each
commit's tests pass on their own.

---

## Yibing

### 1. <Improvement title>

- **Category:**
- **Problem:**
- **Change:**
- **Evidence:** <PR / commit / tests / review link>
- **Files:**

---

## Junho

### 1. <Improvement title>

- **Category:**
- **Problem:**
- **Change:**
- **Evidence:**
- **Files:**

---

## Guransh

### 1. <Improvement title>

- **Category:**
- **Problem:**
- **Change:**
- **Evidence:**
- **Files:**

Two things to know:
- Hashes: 0096051, 022baf0 and the C5 commit will change when you rebase onto main. Update them after the rebase, or use the PR number once the epic PR is open.
- Ownership: each entry describes the code as it is now and doesn't say who wrote it. If teammates co-wrote any of these (for example a review on #146), add their names there.