from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

from backend.app.models.account_model import (
    Account,
    AccountCreationRequest,
    CustomerAccount,
    DeliveryAddress,
    RestaurantAccount,
    StoredAccount,
    StoredAdminAccount,
    StoredCustomerAccount,
    StoredRestaurantAccount,
)

stored_account_adapter = TypeAdapter(StoredAccount)
account_adapter = TypeAdapter(Account)


@pytest.fixture
def customer_record() -> dict[str, Any]:
    return dict(
        id="cust_001",
        full_name="Cara Customer",
        email="cara@example.com",
        phone="250-555-0101",
        is_active=True,
        role="customer",
        password_hash="scrypt$salt$hash",
    )


@pytest.mark.parametrize(
    "role, expected_class",
    [
        ("customer", StoredCustomerAccount),
        ("restaurant_owner", StoredRestaurantAccount),
        ("admin", StoredAdminAccount),
    ],
)
def test_stored_account_picks_class_from_role(customer_record: dict[str, Any], role: str, expected_class: type) -> None:
    account = stored_account_adapter.validate_python(customer_record | {"role": role})

    assert type(account) is expected_class


def test_unknown_role_is_rejected(customer_record: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        stored_account_adapter.validate_python(customer_record | {"role": "chef"})


def test_public_account_drops_password_hash(customer_record: dict[str, Any]) -> None:
    stored = stored_account_adapter.validate_python(customer_record)

    public = account_adapter.validate_python(stored.model_dump())

    assert type(public) is CustomerAccount
    assert "password_hash" not in public.model_dump()


@pytest.mark.parametrize("field", ["full_name", "email", "phone"])
def test_required_text_fields_reject_empty(customer_record: dict[str, Any], field: str) -> None:
    with pytest.raises(ValidationError):
        stored_account_adapter.validate_python(customer_record | {field: ""})


@pytest.mark.parametrize("account_id", ["cust_01", "cust_0001", ""])
def test_id_must_be_eight_characters(customer_record: dict[str, Any], account_id: str) -> None:
    with pytest.raises(ValidationError):
        stored_account_adapter.validate_python(customer_record | {"id": account_id})


def test_list_fields_default_empty_and_are_not_shared(customer_record: dict[str, Any]) -> None:
    public_fields = {key: value for key, value in customer_record.items() if key not in ("role", "password_hash")}
    first_customer = CustomerAccount(**public_fields)
    second_customer = CustomerAccount(**public_fields | {"id": "cust_002"})
    owner = RestaurantAccount(**public_fields | {"id": "ownr_001"})

    first_customer.delivery_addresses.append(DeliveryAddress(label="Home", address="123 Main St"))

    assert second_customer.delivery_addresses == []
    assert owner.owned_restaurant_ids == []


def test_account_creation_request_hides_password() -> None:
    request = AccountCreationRequest(
        full_name="Cara Customer", email="cara@example.com", phone="250-555-0101", password="hunter2"
    )

    assert "hunter2" not in repr(request)
    assert request.password.get_secret_value() == "hunter2"


def test_email_is_trimmed_and_lowercased(customer_record: dict[str, Any]) -> None:
    account = stored_account_adapter.validate_python(customer_record | {"email": "  Cara@Example.COM "})

    assert account.email == "cara@example.com"
