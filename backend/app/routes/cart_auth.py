from typing import Annotated

from fastapi import Depends

from backend.app.dependencies.auth import require_role
from backend.app.models.auth_model import AuthenticatedAccount


def get_authenticated_customer_id(
    account: Annotated[AuthenticatedAccount, Depends(require_role("customer"))],
) -> str:
    return account.id
