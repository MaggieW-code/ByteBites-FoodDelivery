# dependencies

## Purpose

FastAPI dependencies that run before a route's own code. They answer "who is calling?" and
"are they allowed?", so routes stay HTTP-only and services stay free of HTTP.

## Contents

| File | Dependency | Returns | Errors → status |
|---|---|---|---|
| `auth.py` | `get_auth_service` | `AuthService` built from `config.py` paths and token lifetime | none |
| | `get_account_service` | `AccountService` built from the `config.py` accounts and sessions paths | none |
| | `get_bearer_token` | The token from `Authorization: Bearer <token>` | Missing header, wrong scheme, or empty token → 401 |
| | `get_current_account` | `AuthenticatedAccount` for the token | `InvalidTokenError`, `SessionExpiredError` → 401; `AccountDeactivatedError` → 403 |
| | `require_role(*roles)` | A dependency that passes only those roles and returns the account | Wrong role → 403 |

Every 401 carries `WWW-Authenticate: Bearer`. `bearer_scheme` (`HTTPBearer`) also adds the
"Authorize" button to `/docs`.

## How it connects

- Routes declare them: `account: Annotated[AuthenticatedAccount, Depends(get_current_account)]`
  when the route needs the caller, or `dependencies=[Depends(require_role("restaurant_owner"))]`
  when it only needs the gate.
- They call `services/accounts/auth_service.py` and translate its domain errors into HTTP errors, the
  same job routes do for their own services.
- Tests replace `get_auth_service` with `app.dependency_overrides` to point at `tmp_path` files.

## Conventions

- Coarse checks (signed in, role) live here. Rules about specific data (this cart is yours)
  live in the service that owns that data.
- Catch only named domain errors; never `Exception`.
