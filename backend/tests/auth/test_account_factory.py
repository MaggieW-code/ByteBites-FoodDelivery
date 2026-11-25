"""AccountFactory builds new stored accounts: the right class per role, with every default a new account gets."""

import pytest
from pydantic import ValidationError

from backend.app.models.accounts.account_model import (
    AccountCreationRequest,
    Role,
    StoredAdminAccount,
    StoredCustomerAccount,
    StoredRestaurantAccount,
)
from backend.app.services.accounts.account_factory import AccountFactory


def fake_hash(password: str) -> str:
    return f"hashed:{password}"


@pytest.fixture
def account_factory() -> AccountFactory:
    return AccountFactory(hash_password=fake_hash)


@pytest.fixture
def registration() -> AccountCreationRequest:
    return AccountCreationRequest(
        full_name="Nina New", email="nina@example.com", phone="+12505550123", password="nina-password"
    )


def test_create_customer_gives_a_new_active_customer(
    account_factory: AccountFactory, registration: AccountCreationRequest
) -> None:
    customer = account_factory.create(registration, "customer", account_id="acct_new")

    assert type(customer) is StoredCustomerAccount
    assert customer.id == "acct_new"
    assert (customer.full_name, customer.email, customer.phone) == ("Nina New", "nina@example.com", "+12505550123")
    assert customer.is_active is True
    assert customer.delivery_addresses == []


def test_create_stores_only_the_hashed_password(account_factory: AccountFactory, registration: AccountCreationRequest) -> None:
    customer = account_factory.create(registration, "customer", account_id="acct_new")

    assert customer.password_hash == "hashed:nina-password"
    assert "nina-password" not in customer.model_dump_json().replace("hashed:nina-password", "")


@pytest.mark.parametrize(
    "role, stored_class",
    [
        ("customer", StoredCustomerAccount),
        ("restaurant_owner", StoredRestaurantAccount),
        ("admin", StoredAdminAccount),
    ],
    ids=["customer", "owner", "admin"],
)
def test_create_picks_the_stored_class_for_each_role(
    account_factory: AccountFactory, registration: AccountCreationRequest, role: Role, stored_class: type
) -> None:
    account = account_factory.create(registration, role, account_id="acct_new")

    assert type(account) is stored_class
    assert account.role == role


def test_unknown_role_is_rejected(account_factory: AccountFactory, registration: AccountCreationRequest) -> None:
    with pytest.raises(ValidationError):
        account_factory.create(registration, "courier", account_id="acct_new")  # type: ignore[arg-type]
