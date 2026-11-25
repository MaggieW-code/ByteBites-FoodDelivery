from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from backend.app.dependencies.auth import get_account_service, require_role
from backend.app.models.accounts.account_model import (
    Account,
    AccountCreationRequest,
    CreateDeliveryAddressRequest,
    CustomerAccount,
    DeliveryAddress,
    DeliveryAddressId,
    UpdateCustomerRequest,
    UpdateDeliveryAddressRequest,
)
from backend.app.models.accounts.auth_model import AuthenticatedAccount
from backend.app.services.accounts.account_service import (
    AccountService,
    DeliveryAddressNotFoundError,
    EmailAlreadyRegisteredError,
)

router = APIRouter(prefix="/customers", tags=["customers"])

AccountServiceDependency = Annotated[AccountService, Depends(get_account_service)]
CurrentCustomer = Annotated[AuthenticatedAccount, Depends(require_role("customer"))]
DeliveryAddressIdPath = Annotated[
    DeliveryAddressId, Path(description="Delivery address ID, from POST /customers/me/addresses")
]

CUSTOMER_AUTH_RESPONSES: dict[int | str, dict[str, str]] = {
    401: {"description": "Missing, invalid, expired, or signed-out token"},
    403: {"description": "Caller is not a customer, or the account is deactivated"},
}


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
    responses=CUSTOMER_AUTH_RESPONSES,
)
def get_my_profile(customer: CurrentCustomer, account_service: AccountServiceDependency) -> Account:
    """Customer resource: the caller's own customer account, for the profile page.

    Same data as `GET /auth/me` for a customer, but customers only. `PATCH /customers/me` and
    deactivation live beside it. The ID comes from the token, never the URL, so a customer can
    only ever read their own account.
    """
    return account_service.get_account(customer.id)


@router.patch(
    "/me",
    response_model=CustomerAccount,
    description=(
        "Update the signed-in customer's name, email, or phone. Send only the fields to change. "
        "Addresses change through `/customers/me/addresses`; `role`, `is_active` and `password` can't be changed here."
    ),
    responses=CUSTOMER_AUTH_RESPONSES | {409: {"description": "Email is already used by another account"}},
)
def update_my_profile(
    request: UpdateCustomerRequest, customer: CurrentCustomer, account_service: AccountServiceDependency
) -> Account:
    try:
        return account_service.update_customer(customer.id, request)
    except EmailAlreadyRegisteredError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error


@router.post(
    "/me/addresses",
    response_model=DeliveryAddress,
    status_code=status.HTTP_201_CREATED,
    description="Add a delivery address to the signed-in customer. Returns it with its new `id`.",
    responses=CUSTOMER_AUTH_RESPONSES,
)
def add_my_address(
    request: CreateDeliveryAddressRequest, customer: CurrentCustomer, account_service: AccountServiceDependency
) -> DeliveryAddress:
    return account_service.add_address(customer.id, request)


@router.patch(
    "/me/addresses/{address_id}",
    response_model=DeliveryAddress,
    description="Change one of the signed-in customer's addresses. Send only the fields to change.",
    responses=CUSTOMER_AUTH_RESPONSES | {404: {"description": "Address not found for this customer"}},
)
def update_my_address(
    address_id: DeliveryAddressIdPath,
    request: UpdateDeliveryAddressRequest,
    customer: CurrentCustomer,
    account_service: AccountServiceDependency,
) -> DeliveryAddress:
    try:
        return account_service.update_address(customer.id, address_id, request)
    except DeliveryAddressNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error


@router.delete(
    "/me/addresses/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Remove one of the signed-in customer's addresses.",
    responses=CUSTOMER_AUTH_RESPONSES | {404: {"description": "Address not found for this customer"}},
)
def remove_my_address(
    address_id: DeliveryAddressIdPath, customer: CurrentCustomer, account_service: AccountServiceDependency
) -> None:
    try:
        account_service.remove_address(customer.id, address_id)
    except DeliveryAddressNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error


@router.post(
    "/me/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
    description=(
        "Deactivate the signed-in customer's account and sign it out everywhere. "
        "Its tokens stop working (401) and signing in again is refused (403)."
    ),
    responses=CUSTOMER_AUTH_RESPONSES,
)
def deactivate_my_account(customer: CurrentCustomer, account_service: AccountServiceDependency) -> None:
    account_service.deactivate_account(customer.id)
