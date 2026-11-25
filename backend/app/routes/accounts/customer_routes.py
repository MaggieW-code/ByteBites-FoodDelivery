from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.dependencies.auth import get_account_service
from backend.app.models.accounts.account_model import Account, AccountCreationRequest, CustomerAccount
from backend.app.services.accounts.account_service import AccountService, EmailAlreadyRegisteredError

router = APIRouter(prefix="/customers", tags=["customers"])

AccountServiceDependency = Annotated[AccountService, Depends(get_account_service)]


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
