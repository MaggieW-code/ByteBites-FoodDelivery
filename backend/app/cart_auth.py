from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from backend.app.models.authenticated_account_model import AuthenticatedAccount


def get_authenticated_account(request: Request) -> AuthenticatedAccount:
    """Read the current account supplied by server-side authentication."""
    account = getattr(request.state, "authenticated_account", None)
    if not isinstance(account, AuthenticatedAccount):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer authentication required",
        )
    return account


def get_authenticated_customer_id(
    account: Annotated[AuthenticatedAccount, Depends(get_authenticated_account)],
) -> str:
    if account.role != "customer" or not account.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="An active customer account is required",
        )
    return account.id
