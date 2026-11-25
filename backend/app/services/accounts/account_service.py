from uuid import uuid4

from pydantic import TypeAdapter

from backend.app.models.accounts.account_model import (
    Account,
    AccountCreationRequest,
    CreateDeliveryAddressRequest,
    DeliveryAddress,
    Role,
    StoredAccount,
    StoredCustomerAccount,
    UpdateCustomerRequest,
    UpdateDeliveryAddressRequest,
)
from backend.app.repositories.accounts.account_repository import AccountRepository
from backend.app.services.accounts.account_factory import AccountFactory

account_adapter = TypeAdapter(Account)
stored_account_adapter = TypeAdapter(StoredAccount)


class AccountError(Exception):
    pass


class EmailAlreadyRegisteredError(AccountError):
    pass


class AccountNotFoundError(AccountError):
    pass


class DeliveryAddressNotFoundError(AccountError):
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

    def update_customer(self, account_id: str, request: UpdateCustomerRequest) -> Account:
        stored = self.get_stored_customer(account_id)

        changes = request.model_dump(exclude_unset=True)
        if "email" in changes:
            owner_of_email = self.account_repository.get_by_email(changes["email"])
            if owner_of_email is not None and owner_of_email.id != account_id:
                raise EmailAlreadyRegisteredError(f"Email already registered: {changes['email']}")

        # Validate the merged record, so the saved account obeys the same rules as a new one.
        updated = stored_account_adapter.validate_python(stored.model_dump() | changes)
        self.account_repository.update(updated)
        return to_public(updated)

    def add_address(self, account_id: str, request: CreateDeliveryAddressRequest) -> DeliveryAddress:
        customer = self.get_stored_customer(account_id)
        address = DeliveryAddress(id=new_address_id(customer), **request.model_dump())
        self.save_addresses(customer, [*customer.delivery_addresses, address])
        return address

    def update_address(self, account_id: str, address_id: str, request: UpdateDeliveryAddressRequest) -> DeliveryAddress:
        customer = self.get_stored_customer(account_id)
        existing = find_address(customer, address_id)
        updated = existing.model_copy(update=request.model_dump(exclude_unset=True))
        addresses = [updated if address.id == address_id else address for address in customer.delivery_addresses]
        self.save_addresses(customer, addresses)
        return updated

    def remove_address(self, account_id: str, address_id: str) -> None:
        customer = self.get_stored_customer(account_id)
        find_address(customer, address_id)
        self.save_addresses(customer, [address for address in customer.delivery_addresses if address.id != address_id])

    def save_addresses(self, customer: StoredCustomerAccount, addresses: list[DeliveryAddress]) -> None:
        self.account_repository.update(customer.model_copy(update={"delivery_addresses": addresses}))

    def deactivate_account(self, account_id: str) -> Account:
        stored = self.get_stored_account(account_id).model_copy(update={"is_active": False})
        self.account_repository.update(stored)
        return to_public(stored)

    def get_stored_account(self, account_id: str) -> StoredAccount:
        account = self.account_repository.get_by_id(account_id)
        if account is None:
            raise AccountNotFoundError(f"Account '{account_id}' not found")
        return account

    def get_stored_customer(self, account_id: str) -> StoredCustomerAccount:
        account = self.get_stored_account(account_id)
        if not isinstance(account, StoredCustomerAccount):
            raise AccountNotFoundError(f"Customer '{account_id}' not found")
        return account

    def new_account_id(self) -> str:
        account_id = uuid4().hex[:8]
        while self.account_repository.get_by_id(account_id) is not None:
            account_id = uuid4().hex[:8]
        return account_id


def find_address(customer: StoredCustomerAccount, address_id: str) -> DeliveryAddress:
    address = next((address for address in customer.delivery_addresses if address.id == address_id), None)
    if address is None:
        raise DeliveryAddressNotFoundError(f"Delivery address '{address_id}' not found")
    return address


def new_address_id(customer: StoredCustomerAccount) -> str:
    """Unique within this customer only: address IDs are always looked up through their customer."""
    taken_ids = {address.id for address in customer.delivery_addresses}
    address_id = uuid4().hex[:8]
    while address_id in taken_ids:
        address_id = uuid4().hex[:8]
    return address_id


def to_public(stored: StoredAccount) -> Account:
    return account_adapter.validate_python(stored.model_dump())
