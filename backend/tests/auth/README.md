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
| `conftest.py` | Auth-only fixtures: `account_records` (active customer, inactive customer, owner) and `session_records` → `accounts_file`, `sessions_file` → `account_repository`, `session_repository` |

## How it connects

- Tests `backend/app/models/account_model.py`, `backend/app/models/auth_model.py`,
  `backend/app/repositories/account_repository.py` and `session_repository.py`.
- `conftest.py` here builds on `write_json` from `backend/tests/conftest.py`. Its fixtures move
  to the root conftest once tests outside this folder need them (route tests for protected
  restaurant and menu endpoints).

## Conventions

- File names stay unique across the whole suite (`test_auth_<layer>.py`), because pytest's
  default import mode fails on two test files with the same name in different folders.
- Cover roles with `@pytest.mark.parametrize(..., ids=[...])`, so `pytest -k owner` selects one role.
