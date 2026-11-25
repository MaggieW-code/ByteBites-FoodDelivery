from uuid import uuid4

from pydantic import TypeAdapter

from backend.app.models.accounts.account_model import Account, AccountCreationRequest, Role, StoredAccount
from backend.app.repositories.accounts.account_repository import AccountRepository
from backend.app.services.accounts.account_factory import AccountFactory

account_adapter = TypeAdapter(Account)


class AccountError(Exception):
    pass


class EmailAlreadyRegisteredError(AccountError):
    pass


class AccountNotFoundError(AccountError):
    pass


class AccountService:
    def __init__(self, account_repository: AccountRepository, *, account_factory: AccountFactory | None = None) -> None:
        self.account_repository = account_repository
        self.account_factory = account_factory or AccountFactory()

    def register_account(self, request: AccountCreationRequest, role: Role = "customer") -> Account:
        if self.account_repository.get_by_email(request.email) is not None:
            raise EmailAlreadyRegisteredError(f"Email already registered: {request.email}")

        stored = self.account_factory.create(request, role, account_id=self.new_account_id())
        self.account_repository.add(stored)
        return to_public(stored)

    def get_account(self, account_id: str) -> Account:
        return to_public(self.get_stored_account(account_id))

    def deactivate_account(self, account_id: str) -> Account:
        stored = self.get_stored_account(account_id).model_copy(update={"is_active": False})
        self.account_repository.update(stored)
        return to_public(stored)

    def get_stored_account(self, account_id: str) -> StoredAccount:
        account = self.account_repository.get_by_id(account_id)
        if account is None:
            raise AccountNotFoundError(f"Account '{account_id}' not found")
        return account

    def new_account_id(self) -> str:
        account_id = uuid4().hex[:8]
        while self.account_repository.get_by_id(account_id) is not None:
            account_id = uuid4().hex[:8]
        return account_id


def to_public(stored: StoredAccount) -> Account:
    return account_adapter.validate_python(stored.model_dump())
