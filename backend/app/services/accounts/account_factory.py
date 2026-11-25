"""Builds new stored accounts, so the defaults every new account gets live in one place."""

from collections.abc import Callable

from pydantic import TypeAdapter

from backend.app.models.accounts.account_model import AccountCreationRequest, Role, StoredAccount
from backend.app.services.accounts import password_hashing

stored_account_adapter = TypeAdapter(StoredAccount)


class AccountFactory:
    """Turns a registration request into a new stored account for a role.

    The stored class comes from the `StoredAccount` union's `role` discriminator. The password hasher is
    injected so tests can make it fast and predictable.
    """

    def __init__(self, *, hash_password: Callable[[str], str] = password_hashing.hash_password) -> None:
        self.hash_password = hash_password

    def create(self, request: AccountCreationRequest, role: Role, *, account_id: str) -> StoredAccount:
        return stored_account_adapter.validate_python(
            {
                "id": account_id,
                "role": role,
                "full_name": request.full_name,
                "email": request.email,
                "phone": request.phone,
                "is_active": True,
                "password_hash": self.hash_password(request.password.get_secret_value()),
            }
        )
