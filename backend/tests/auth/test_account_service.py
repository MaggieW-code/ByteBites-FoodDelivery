import pytest

from backend.app.models.accounts.account_model import AccountCreationRequest, CustomerAccount, RestaurantAccount
from backend.app.models.accounts.auth_model import SignInRequest
from backend.app.repositories.accounts.account_repository import AccountRepository
from backend.app.services.accounts.account_service import (
    AccountNotFoundError,
    AccountService,
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
