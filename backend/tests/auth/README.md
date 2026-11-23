# auth

## Purpose

Tests for accounts, sign-in, and sessions (epic #115). Roles are test parameters here, not
folders: one test covers how a rule treats each role.

## Contents

| File | Tests |
|---|---|
| `test_account_model.py` | `StoredAccount` picks the class from `role`, unknown roles are rejected, public accounts drop `password_hash`, required text and 8-character IDs, list defaults, hidden passwords, email trimmed and lowercased |
| `test_auth_model.py` | `AuthenticatedAccount` is frozen and strict, `SignInRequest` hides the password and normalizes the email, `Session` round-trips through JSON and rejects times without a timezone |
| `test_account_repository.py` | Lookups by ID and email, stored class per role, add and update persist across a new repository, IDs stay stable, missing and malformed files raise |
| `test_session_repository.py` | Lookup by token hash, add keeps timezones, delete removes only one session, a missing file means no sessions, malformed files raise |
| `test_password_hashing.py` | The hash hides the password, verify accepts only the right one, salts differ, malformed hashes raise |
| `test_auth_service.py` | Sign in (token, expiry, only the hash stored, same error for wrong password and unknown email, deactivated blocked), resolve token (unknown, expired and removed, deactivated), sign out, register, get and deactivate accounts |
| `test_auth_dependencies.py` | On a small probe app: valid token identifies the caller, missing or bad tokens are 401 with `WWW-Authenticate`, expired 401, deactivated 403, `require_role` per role, bearer scheme in OpenAPI |
| `test_auth_routes.py` | On the real app: sign in returns a working token, wrong password and unknown email give the same 401, deactivated 403, incomplete body 422; `/auth/me` returns the public profile per role with no `password_hash`, 401 without a token; sign-out is 204 (also for unknown tokens and twice), ends only that session, 401 without a header |
| `test_auth_config.py` | Account and session paths (default and override), token lifetime (default, override, bad values rejected) |
| `conftest.py` | Auth-only fixtures: `test_password_hash` (one real scrypt hash per session), `account_records` (active customer, inactive customer, owner) and `session_records` → files → repositories, `clock` (a `FakeClock`) → `auth_service`. `client` extends the root `client` so `get_auth_service` returns this test's `auth_service`. `auth_headers(email)` is a factory fixture: it signs in and returns the `Authorization: Bearer` header |
| `auth_helpers.py` | Plain values tests import: `TEST_PASSWORD`, `TOKEN_LIFETIME`, `FakeClock`. Never import from `conftest.py` |

## How it connects

- Tests the auth models, repositories, `services/auth_service.py`, `services/password_hashing.py`,
  `dependencies/auth.py`, `routes/auth_routes.py` and the auth getters in `config.py`.
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
