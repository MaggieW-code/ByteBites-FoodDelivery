# auth

## Purpose

Tests for accounts, sign-in, and sessions (epic #115) and customer accounts (epic #114). Roles are test parameters here, not
folders: one test covers how a rule treats each role.

## Contents

| File | Tests |
|---|---|
| `test_account_model.py` | `StoredAccount` picks the class from `role`, unknown roles are rejected, public accounts drop `password_hash`, required text and 8-character IDs, list defaults, hidden passwords, email trimmed and lowercased, invalid or reserved-domain emails rejected, phones in common formats stored as E.164, invalid and non-Canadian phones rejected |
| `test_auth_model.py` | `AuthenticatedAccount` is frozen and strict, `SignInRequest` hides the password and normalizes the email but doesn't check its format (still rejects empty, oversized and non-text), `Session` round-trips through JSON and rejects times without a timezone |
| `test_account_repository.py` | Lookups by ID and email, stored class per role, add and update persist across a new repository, IDs stay stable, missing and malformed files raise, the real seeded `data/accounts.json` still loads |
| `test_session_repository.py` | Lookup by token hash, add keeps timezones, delete removes only one session, a missing file means no sessions, malformed files raise |
| `test_password_hashing.py` | The hash hides the password, verify accepts only the right one, salts differ, malformed hashes raise |
| `test_auth_service.py` | Sign in (token, expiry, only the hash stored, same error for wrong password and unknown email, deactivated blocked), resolve token (unknown, expired and removed, deactivated), sign out |
| `test_account_service.py` | Register (customer that can sign in, owner, unique IDs, existing email rejected in any case or spacing), get returns the public account, unknown IDs raise |
| `test_auth_dependencies.py` | On a small probe app: valid token identifies the caller, missing or bad tokens are 401 with `WWW-Authenticate`, expired 401, deactivated 403, `require_role` per role, bearer scheme in OpenAPI |
| `test_auth_routes.py` | On the real app: sign in returns a working token, wrong password, unknown email and malformed or reserved-domain email give the same 401, deactivated 403, incomplete body 422; `/auth/me` returns the public profile per role with no `password_hash`, 401 without a token; sign-out is 204 (also for unknown tokens and twice), ends only that session, 401 without a header |
| `test_account_factory.py` | `AccountFactory` builds the stored class for each role with the given ID, unknown roles are rejected, new accounts are active with no addresses, only the hashed password is stored (fake hasher, no scrypt) |
| `test_customer_routes.py` | On the real app: `POST /customers` returns 201 with the public customer, saves a hashed password, never returns the password, ignores a requested `role`, existing email (any case or spacing) is 409, invalid bodies (including a bad email or phone) are 422, rejected requests save nothing; C2: a registered customer signs in (any email case or spacing) and `/auth/me` returns the same profile, a wrong password is 401; C3: `GET /customers/me` returns the caller's profile, 401 without a token, 403 for an owner or a deactivated customer |
| `test_auth_config.py` | Account and session paths (default and override), token lifetime (default, override, bad values rejected) |
| `conftest.py` | Auth-only fixtures: `test_password_hash` (one real scrypt hash per session), `account_records` (active customer, inactive customer, owner) and `session_records` → files → repositories, `clock` (a `FakeClock`) → `auth_service`, and `account_service` on the same account repository. `client` extends the root `client` so `get_auth_service` and `get_account_service` return this test's services. `auth_headers(email)` is a factory fixture: it signs in and returns the `Authorization: Bearer` header |
| `auth_helpers.py` | Plain values tests import: `TEST_PASSWORD`, `TOKEN_LIFETIME`, `FakeClock`. Never import from `conftest.py` |

## How it connects

- Tests the auth models, repositories, `services/accounts/auth_service.py`, `services/accounts/account_service.py`,
  `services/accounts/account_factory.py`, `services/accounts/password_hashing.py`,
  `dependencies/auth.py`, `routes/accounts/auth_routes.py` and the auth getters in `config.py`.
- Route tests swap the service through FastAPI's own seam:
  `monkeypatch.setitem(app.dependency_overrides, get_auth_service, ...)`, undone after each
  test. `client` and `auth_headers` share one `auth_service` per test, so a token signed in
  by `auth_headers` resolves in the route, and `clock.advance(...)` expires it there too.
- Time is injected: `AuthService` takes a `clock`, and tests pass a `FakeClock` they advance,
  so expiry is tested without sleeping.
- `conftest.py` here builds on `write_json` from `backend/tests/conftest.py`. Its fixtures move
  to the root conftest once tests outside this folder need them (route tests for protected
  restaurant and menu endpoints).

## Conventions

- File names stay unique across the whole suite (`test_auth_<layer>.py`), because pytest's
  default import mode fails on two test files with the same name in different folders.
- Cover roles with `@pytest.mark.parametrize(..., ids=[...])`, so `pytest -k owner` selects one role.
