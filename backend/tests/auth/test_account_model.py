from typing import Any

import pytest
from pydantic import TypeAdapter, ValidationError

from backend.app.models.accounts.account_model import (
    Account,
    AccountCreationRequest,
    CustomerAccount,
    DeliveryAddress,
    RestaurantAccount,
    StoredAccount,
    StoredAdminAccount,
    StoredCustomerAccount,
    StoredRestaurantAccount,
    UpdateCustomerRequest,
    UpdateDeliveryAddressRequest,
)

stored_account_adapter = TypeAdapter(StoredAccount)
account_adapter = TypeAdapter(Account)


@pytest.fixture
def customer_record() -> dict[str, Any]:
    return dict(
        id="cust_001",
        full_name="Cara Customer",
        email="cara@example.com",
        phone="+12505550101",
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


@pytest.mark.parametrize(
    "phone",
    ["250-222-1234", "(250) 222-1234", " 250.222.1234 ", "2502221234", "12502221234", "+1 250 222 1234"],
    ids=["dashes", "brackets", "dots-and-spaces", "ten-digits", "with-country-code", "international"],
)
def test_phone_is_stored_as_e164(customer_record: dict[str, Any], phone: str) -> None:
    account = stored_account_adapter.validate_python(customer_record | {"phone": phone})

    assert account.phone == "+12502221234"


@pytest.mark.parametrize(
    "phone",
    ["02502221234", "250-222-12345", "123", "abc", "+12125551234", "+442071838750", 2502221234],
    ids=["not-a-real-number", "too-many-digits", "too-short", "letters", "us-number", "uk-number", "integer"],
)
def test_phone_rejects_invalid_and_non_canadian_numbers(customer_record: dict[str, Any], phone: Any) -> None:
    with pytest.raises(ValidationError):
        stored_account_adapter.validate_python(customer_record | {"phone": phone})

    with pytest.raises(ValidationError):
        AccountCreationRequest(full_name="Cara Customer", email="cara@example.com", phone=phone, password="hunter2!")


@pytest.mark.parametrize(
    "email",
    [
        "cara",
        "cara@",
        "@example.com",
        "cara@example",
        "cara example@example.com",
        "cara@bytebites.test",
        "x" * 250 + "@example.com",
    ],
    ids=["no-at", "no-domain", "no-local-part", "no-dot", "space", "reserved-domain", "too-long"],
)
def test_email_must_be_a_valid_address(customer_record: dict[str, Any], email: str) -> None:
    with pytest.raises(ValidationError):
        stored_account_adapter.validate_python(customer_record | {"email": email})


@pytest.mark.parametrize("account_id", ["cust_01", "cust_0001", ""])
def test_id_must_be_eight_characters(customer_record: dict[str, Any], account_id: str) -> None:
    with pytest.raises(ValidationError):
        stored_account_adapter.validate_python(customer_record | {"id": account_id})


def test_list_fields_default_empty_and_are_not_shared(customer_record: dict[str, Any]) -> None:
    public_fields = {key: value for key, value in customer_record.items() if key not in ("role", "password_hash")}
    first_customer = CustomerAccount(**public_fields)
    second_customer = CustomerAccount(**public_fields | {"id": "cust_002"})
    owner = RestaurantAccount(**public_fields | {"id": "ownr_001"})

    first_customer.delivery_addresses.append(DeliveryAddress(id="addr_001", label="Home", address="123 Main St"))

    assert second_customer.delivery_addresses == []
    assert owner.owned_restaurant_ids == []


def test_account_creation_request_hides_password() -> None:
    request = AccountCreationRequest(
        full_name="Cara Customer", email="cara@example.com", phone="+12505550101", password="hunter2!"
    )

    assert "hunter2!" not in repr(request)
    assert request.password.get_secret_value() == "hunter2!"


@pytest.mark.parametrize("password", ["1234567", "x" * 129], ids=["too-short", "too-long"])
def test_account_creation_request_limits_password_length(password: str) -> None:
    with pytest.raises(ValidationError):
        AccountCreationRequest(full_name="Cara Customer", email="cara@example.com", phone="+12505550101", password=password)


def test_email_is_trimmed_and_lowercased(customer_record: dict[str, Any]) -> None:
    account = stored_account_adapter.validate_python(customer_record | {"email": "  Cara@Example.COM "})

    assert account.email == "cara@example.com"


# --- UpdateCustomerRequest (C4) ---


def test_update_request_keeps_only_the_fields_sent() -> None:
    request = UpdateCustomerRequest(phone="(250) 555-0199")

    assert request.model_dump(exclude_unset=True) == {"phone": "+12505550199"}


@pytest.mark.parametrize(
    "body",
    [{}, {"role": "admin"}, {"delivery_addresses": []}, {"full_name": None}],
    ids=["empty", "only-unknown-fields", "only-addresses", "null-name"],
)
def test_update_request_needs_a_real_change(body: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        UpdateCustomerRequest(**body)


@pytest.mark.parametrize(
    "body",
    [
        {"full_name": ""},
        {"email": "not-an-email"},
        {"phone": "12501233211"},
    ],
    ids=["empty-name", "bad-email", "bad-phone"],
)
def test_update_request_uses_the_registration_rules(body: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        UpdateCustomerRequest(**body)


# --- delivery addresses (C4) ---


def test_stored_address_needs_an_eight_character_id() -> None:
    with pytest.raises(ValidationError):
        DeliveryAddress(label="Home", address="1 Main St")
    with pytest.raises(ValidationError):
        DeliveryAddress(id="addr_1", label="Home", address="1 Main St")


@pytest.mark.parametrize(
    "body",
    [{}, {"label": None}, {"label": ""}, {"address": ""}],
    ids=["empty", "null-label", "empty-label", "empty-address"],
)
def test_address_update_needs_a_real_non_empty_change(body: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        UpdateDeliveryAddressRequest(**body)
