from dataclasses import dataclass
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status

from backend.app.dependencies.auth import require_role
from backend.app.models.auth_model import AuthenticatedAccount


@dataclass(frozen=True)
class AuthenticatedCustomer:
    customer_id: str
    role: Literal["customer"] = "customer"


def get_current_active_customer(
    account: Annotated[AuthenticatedAccount, Depends(require_role("customer"))],
) -> AuthenticatedCustomer:
    if not account.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "An active customer account is required")
    return AuthenticatedCustomer(customer_id=account.id)


CurrentCustomer = Annotated[AuthenticatedCustomer, Depends(get_current_active_customer)]
