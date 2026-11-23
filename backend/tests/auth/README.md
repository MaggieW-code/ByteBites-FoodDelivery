# auth

## Purpose

Tests for accounts, sign-in, and sessions (epic #115). Roles are test parameters here, not
folders: one test covers how a rule treats each role.

## Contents

| File | Tests |
|---|---|
| `test_account_model.py` | `StoredAccount` picks the class from `role`, unknown roles are rejected, public accounts drop `password_hash`, required text and 8-character IDs, list defaults, hidden passwords, email trimmed and lowercased |
| `test_auth_model.py` | `AuthenticatedAccount` is frozen and strict, `SignInRequest` hides the password and normalizes the email, `Session` round-trips through JSON and rejects times without a timezone |

## How it connects

- Tests `backend/app/models/account_model.py` and `backend/app/models/auth_model.py`.
- The shared fixtures in `backend/tests/conftest.py` apply here too. Records used only by one
  file stay in that file until a second file needs them.

## Conventions

- File names stay unique across the whole suite (`test_auth_<layer>.py`), because pytest's
  default import mode fails on two test files with the same name in different folders.
- Cover roles with `@pytest.mark.parametrize(..., ids=[...])`, so `pytest -k owner` selects one role.
