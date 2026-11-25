"""FastAPI dependencies that answer "who is calling?" (401) and "may they?" (403) before a route runs."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.config import get_accounts_data_path, get_auth_token_lifetime, get_sessions_data_path
from backend.app.models.accounts.account_model import Role
from backend.app.models.accounts.auth_model import AuthenticatedAccount
from backend.app.repositories.accounts.account_repository import AccountRepository
from backend.app.repositories.accounts.session_repository import SessionRepository
from backend.app.services.accounts.account_service import AccountService
from backend.app.services.accounts.auth_service import (
    AccountDeactivatedError,
    AuthService,
    InvalidTokenError,
    SessionExpiredError,
)

bearer_scheme = HTTPBearer(auto_error=False, description="Token from POST /auth/sign-in")
BEARER_CHALLENGE = {"WWW-Authenticate": "Bearer"}


def get_auth_service() -> AuthService:
    return AuthService(
        AccountRepository(get_accounts_data_path()),
        SessionRepository(get_sessions_data_path()),
        token_lifetime=get_auth_token_lifetime(),
    )


def get_account_service() -> AccountService:
    return AccountService(AccountRepository(get_accounts_data_path()), SessionRepository(get_sessions_data_path()))


def get_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> str:
    if credentials is None or not credentials.credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required", headers=BEARER_CHALLENGE)
    return credentials.credentials


def get_current_account(
    token: Annotated[str, Depends(get_bearer_token)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthenticatedAccount:
    try:
        return auth_service.resolve_token(token)
    except (InvalidTokenError, SessionExpiredError) as error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(error), headers=BEARER_CHALLENGE) from error
    except AccountDeactivatedError as error:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(error)) from error


def require_role(*allowed_roles: Role) -> Callable[[AuthenticatedAccount], AuthenticatedAccount]:
    """Build a dependency that lets only `allowed_roles` through: `Depends(require_role("restaurant_owner"))`."""

    def check_role(account: Annotated[AuthenticatedAccount, Depends(get_current_account)]) -> AuthenticatedAccount:
        if account.role not in allowed_roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Requires role: {', '.join(allowed_roles)}")
        return account

    return check_role
