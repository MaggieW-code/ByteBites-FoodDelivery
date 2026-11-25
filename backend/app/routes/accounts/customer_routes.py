from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.dependencies.auth import get_account_service, require_role
from backend.app.models.accounts.account_model import Account, AccountCreationRequest, CustomerAccount
from backend.app.models.accounts.auth_model import AuthenticatedAccount
from backend.app.services.accounts.account_service import AccountService, EmailAlreadyRegisteredError

router = APIRouter(prefix="/customers", tags=["customers"])

AccountServiceDependency = Annotated[AccountService, Depends(get_account_service)]
CurrentCustomer = Annotated[AuthenticatedAccount, Depends(require_role("customer"))]


@router.post(
    "",
    response_model=CustomerAccount,
    status_code=status.HTTP_201_CREATED,
    description="Register a new customer account. Sign in afterwards with `POST /auth/sign-in`.",
    responses={409: {"description": "Email is already registered"}},
)
def register_customer(request: AccountCreationRequest, account_service: AccountServiceDependency) -> Account:
    try:
        return account_service.register_account(request, role="customer")
    except EmailAlreadyRegisteredError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error


@router.get(
    "/me",
    response_model=CustomerAccount,
    description="Return the signed-in customer's own profile, including delivery addresses.",
    responses={
        401: {"description": "Missing, invalid, expired, or signed-out token"},
        403: {"description": "Caller is not a customer, or the account is deactivated"},
    },
)
def get_my_profile(customer: CurrentCustomer, account_service: AccountServiceDependency) -> Account:
    """Customer resource: the caller's own customer account, for the profile page.

    Same data as `GET /auth/me` for a customer, but customers only. `PATCH /customers/me` and
    deactivation live beside it. The ID comes from the token, never the URL, so a customer can
    only ever read their own account.
    """
    return account_service.get_account(customer.id)
