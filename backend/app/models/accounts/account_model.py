from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, BeforeValidator, EmailStr, Field, SecretStr, model_validator
from pydantic_extra_types.phone_numbers import PhoneNumberValidator


def normalize_email(value: object) -> object:
    """Trim and lowercase the whole address, so lookups and the duplicate check ignore case."""
    return value.strip().lower() if isinstance(value, str) else value


EightCharId: TypeAlias = Annotated[str, Field(strict=True, min_length=8, max_length=8)]
Role: TypeAlias = Literal["customer", "restaurant_owner", "admin"]
NonEmptyText: TypeAlias = Annotated[str, Field(strict=True, min_length=1)]
Email: TypeAlias = Annotated[EmailStr, BeforeValidator(normalize_email)]
# Parsed with libphonenumber and stored as E.164: "(250) 222-1234" becomes "+12502221234".
PhoneNumber: TypeAlias = Annotated[
    str, PhoneNumberValidator(supported_regions=["CA"], default_region="CA", number_format="E164")
]


class AccountCreationRequest(BaseModel):
    full_name: NonEmptyText
    email: Email
    phone: PhoneNumber
    password: Annotated[SecretStr, Field(min_length=8, max_length=128)]


DeliveryAddressId: TypeAlias = EightCharId


class PartialUpdateRequest(BaseModel):
    """Base for PATCH bodies: send only the fields to change, at least one, and never `null`."""

    @model_validator(mode="after")
    def require_a_change_without_nulls(self) -> "PartialUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("Send at least one field to update")
        null_fields = sorted(field for field in self.model_fields_set if getattr(self, field) is None)
        if null_fields:
            raise ValueError(f"Fields cannot be null: {', '.join(null_fields)}")
        return self


class DeliveryAddressFields(BaseModel):
    label: NonEmptyText
    address: NonEmptyText


class CreateDeliveryAddressRequest(DeliveryAddressFields):
    pass


class UpdateDeliveryAddressRequest(PartialUpdateRequest):
    label: NonEmptyText | None = None
    address: NonEmptyText | None = None


class DeliveryAddress(DeliveryAddressFields):
    """A saved address. The ID is unique within its customer, so one address can be edited or removed."""

    id: DeliveryAddressId


class UpdateCustomerRequest(PartialUpdateRequest):
    """PATCH body for the customer's own details. Addresses change through `/customers/me/addresses`.

    Fields not declared here (`role`, `is_active`, `password`, `id`, `delivery_addresses`) are
    ignored, so a customer can't change them here.
    """

    full_name: NonEmptyText | None = None
    email: Email | None = None
    phone: PhoneNumber | None = None


class AccountBase(BaseModel):
    """Fields every role shares. Safe to return from the API: holds no credentials."""

    id: EightCharId
    full_name: NonEmptyText
    email: Email
    phone: PhoneNumber
    is_active: bool = Field(strict=True)


class CustomerAccount(AccountBase):
    role: Literal["customer"] = "customer"
    delivery_addresses: list[DeliveryAddress] = Field(default_factory=list)


class RestaurantAccount(AccountBase):
    role: Literal["restaurant_owner"] = "restaurant_owner"
    owned_restaurant_ids: list[EightCharId] = Field(default_factory=list)


class AdminAccount(AccountBase):
    role: Literal["admin"] = "admin"


class StoredCredentials(BaseModel):
    """Mixed into stored records only, so no response model can ever carry a password hash."""

    password_hash: NonEmptyText


class StoredCustomerAccount(CustomerAccount, StoredCredentials):
    pass


class StoredRestaurantAccount(RestaurantAccount, StoredCredentials):
    pass


class StoredAdminAccount(AdminAccount, StoredCredentials):
    pass


# Type Alias

StoredAccount: TypeAlias = Annotated[
    StoredCustomerAccount | StoredRestaurantAccount | StoredAdminAccount,
    Field(discriminator="role"),
]

Account: TypeAlias = Annotated[CustomerAccount | RestaurantAccount | AdminAccount, Field(discriminator="role")]
