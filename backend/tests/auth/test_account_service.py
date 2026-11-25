import pytest

from backend.app.models.accounts.account_model import (
    AccountCreationRequest,
    CreateDeliveryAddressRequest,
    CustomerAccount,
    RestaurantAccount,
    UpdateCustomerRequest,
    UpdateDeliveryAddressRequest,
)
from backend.app.models.accounts.auth_model import SignInRequest
from backend.app.repositories.accounts.account_repository import AccountRepository
from backend.app.services.accounts.account_service import (
    AccountNotFoundError,
    AccountService,
    DeliveryAddressNotFoundError,
    EmailAlreadyRegisteredError,
)
from backend.app.services.accounts.auth_service import AuthService
from backend.app.services.accounts.password_hashing import verify_password


def make_registration(email: str = "nina@example.com") -> AccountCreationRequest:
    return AccountCreationRequest(full_name="Nina New", email=email, phone="+12505550123", password="nina-password")


def test_register_creates_customer_that_can_sign_in(
    account_service: AccountService, auth_service: AuthService, account_repository: AccountRepository
) -> None:
    account = account_service.register_account(make_registration())

    assert type(account) is CustomerAccount
    assert len(account.id) == 8
    assert "password_hash" not in account.model_dump()
    assert verify_password("nina-password", account_repository.get_by_id(account.id).password_hash)
    assert auth_service.sign_in(SignInRequest(email="nina@example.com", password="nina-password")).access_token


def test_register_can_create_an_owner(account_service: AccountService) -> None:
    account = account_service.register_account(make_registration(), role="restaurant_owner")

    assert type(account) is RestaurantAccount


def test_each_registration_gets_its_own_id(account_service: AccountService) -> None:
    first = account_service.register_account(make_registration("first@example.com"))
    second = account_service.register_account(make_registration("second@example.com"))

    assert first.id != second.id


@pytest.mark.parametrize("email", ["cara@example.com", " CARA@Example.com "])
def test_register_rejects_an_existing_email(account_service: AccountService, email: str) -> None:
    with pytest.raises(EmailAlreadyRegisteredError):
        account_service.register_account(make_registration(email))


def test_get_account_returns_public_account(account_service: AccountService) -> None:
    account = account_service.get_account("cust_001")

    assert type(account) is CustomerAccount
    assert "password_hash" not in account.model_dump()


@pytest.mark.parametrize("method", ["get_account", "deactivate_account"])
def test_unknown_account_raises(account_service: AccountService, method: str) -> None:
    with pytest.raises(AccountNotFoundError):
        getattr(account_service, method)("nope_000")


# --- update customer (C4) ---


def test_update_changes_only_the_fields_sent(account_service: AccountService) -> None:
    before = account_service.get_account("cust_001")

    after = account_service.update_customer("cust_001", UpdateCustomerRequest(full_name="Cara Renamed"))

    assert after.full_name == "Cara Renamed"
    assert after.model_dump(exclude={"full_name"}) == before.model_dump(exclude={"full_name"})


def test_update_is_saved_and_keeps_the_password(
    account_service: AccountService, account_repository: AccountRepository
) -> None:
    password_hash_before = account_repository.get_by_id("cust_001").password_hash

    account_service.update_customer("cust_001", UpdateCustomerRequest(phone="250-555-0199"))

    stored = account_repository.get_by_id("cust_001")
    assert stored.phone == "+12505550199"
    assert stored.password_hash == password_hash_before


@pytest.mark.parametrize("email", ["omar@example.com", " OMAR@Example.com "], ids=["same", "case-and-spaces"])
def test_update_rejects_an_email_used_by_another_account(account_service: AccountService, email: str) -> None:
    with pytest.raises(EmailAlreadyRegisteredError):
        account_service.update_customer("cust_001", UpdateCustomerRequest(email=email))


def test_update_allows_keeping_your_own_email(account_service: AccountService) -> None:
    after = account_service.update_customer("cust_001", UpdateCustomerRequest(email=" CARA@example.com "))

    assert after.email == "cara@example.com"


@pytest.mark.parametrize("account_id", ["nope_000", "ownr_001"], ids=["unknown", "not-a-customer"])
def test_update_needs_an_existing_customer(account_service: AccountService, account_id: str) -> None:
    with pytest.raises(AccountNotFoundError):
        account_service.update_customer(account_id, UpdateCustomerRequest(full_name="Nobody"))


# --- delivery addresses (C4) ---

HOME = CreateDeliveryAddressRequest(label="Home", address="1 Main St")
WORK = CreateDeliveryAddressRequest(label="Work", address="2 Office Rd")


def test_add_address_appends_and_keeps_the_others(account_service: AccountService) -> None:
    home = account_service.add_address("cust_001", HOME)
    work = account_service.add_address("cust_001", WORK)

    assert len(home.id) == 8
    assert home.id != work.id
    assert account_service.get_account("cust_001").delivery_addresses == [home, work]


def test_update_address_changes_only_that_address(account_service: AccountService) -> None:
    home = account_service.add_address("cust_001", HOME)
    work = account_service.add_address("cust_001", WORK)

    updated = account_service.update_address("cust_001", home.id, UpdateDeliveryAddressRequest(address="9 New Ave"))

    assert (updated.id, updated.label, updated.address) == (home.id, "Home", "9 New Ave")
    assert account_service.get_account("cust_001").delivery_addresses == [updated, work]


def test_remove_address_removes_only_that_address(account_service: AccountService) -> None:
    home = account_service.add_address("cust_001", HOME)
    work = account_service.add_address("cust_001", WORK)

    account_service.remove_address("cust_001", home.id)

    assert account_service.get_account("cust_001").delivery_addresses == [work]


@pytest.mark.parametrize("method", ["update_address", "remove_address"])
def test_unknown_address_raises(account_service: AccountService, method: str) -> None:
    arguments = ("cust_001", "nope_000") + ((UpdateDeliveryAddressRequest(label="X"),) if method == "update_address" else ())

    with pytest.raises(DeliveryAddressNotFoundError):
        getattr(account_service, method)(*arguments)


def test_addresses_are_only_for_customers(account_service: AccountService) -> None:
    with pytest.raises(AccountNotFoundError):
        account_service.add_address("ownr_001", HOME)
