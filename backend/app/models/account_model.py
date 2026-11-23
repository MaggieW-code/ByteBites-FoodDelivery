from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, Field, SecretStr, StringConstraints

EightCharId: TypeAlias = Annotated[str, Field(strict=True, min_length=8, max_length=8)]
Role: TypeAlias = Literal["customer", "restaurant_owner", "admin"]
NonEmptyText: TypeAlias = Annotated[str, Field(strict=True, min_length=1)]
Email: TypeAlias = Annotated[
    str, StringConstraints(strict=True, strip_whitespace=True, to_lower=True, min_length=3, max_length=254)
]


class AccountCreationRequest(BaseModel):
    full_name: NonEmptyText
    email: Email
    phone: NonEmptyText
    password: SecretStr


class DeliveryAddress(BaseModel):
    label: NonEmptyText
    address: NonEmptyText


class AccountBase(BaseModel):
    """Fields every role shares. Safe to return from the API: holds no credentials."""

    id: EightCharId
    full_name: NonEmptyText
    email: Email
    phone: NonEmptyText
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
