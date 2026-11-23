from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.dependencies.auth import BEARER_CHALLENGE, get_auth_service, get_bearer_token, get_current_account
from backend.app.models.account_model import Account
from backend.app.models.auth_model import AuthenticatedAccount, SignInRequest, TokenResponse
from backend.app.services.auth_service import AccountDeactivatedError, AuthService, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["auth"])

AuthServiceDependency = Annotated[AuthService, Depends(get_auth_service)]


@router.post(
    "/sign-in",
    response_model=TokenResponse,
    description="Exchange an email and password for a bearer token. Send it back as `Authorization: Bearer <token>`.",
    responses={
        401: {"description": "Invalid email or password"},
        403: {"description": "Account is deactivated"},
    },
)
def sign_in(request: SignInRequest, auth_service: AuthServiceDependency) -> TokenResponse:
    try:
        return auth_service.sign_in(request)
    except InvalidCredentialsError as error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(error), headers=BEARER_CHALLENGE) from error
    except AccountDeactivatedError as error:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(error)) from error


@router.get(
    "/me",
    response_model=Account,
    description="Return the signed-in caller's public profile. Never includes the password hash.",
    responses={
        401: {"description": "Missing, invalid, expired, or signed-out token"},
        403: {"description": "Account is deactivated"},
    },
)
def me(account: Annotated[AuthenticatedAccount, Depends(get_current_account)], auth_service: AuthServiceDependency) -> Account:
    return auth_service.get_account(account.id)


@router.post(
    "/sign-out",
    status_code=status.HTTP_204_NO_CONTENT,
    description="End the session for this token. Succeeds even if the token is unknown or already signed out.",
    responses={401: {"description": "Missing bearer token"}},
)
def sign_out(token: Annotated[str, Depends(get_bearer_token)], auth_service: AuthServiceDependency) -> None:
    auth_service.sign_out(token)
