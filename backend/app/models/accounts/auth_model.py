from typing import Annotated, Literal, TypeAlias

from pydantic import AwareDatetime, BaseModel, ConfigDict, SecretStr, StringConstraints

from backend.app.models.accounts.account_model import EightCharId, NonEmptyText, Role

# For lookups only (sign-in): no format check, so an address stored under older rules can still sign in,
# and a malformed one gets the same 401 as an unknown one instead of a 422. Registration uses Email.
LoginEmail: TypeAlias = Annotated[
    str, StringConstraints(strict=True, strip_whitespace=True, to_lower=True, min_length=1, max_length=254)
]


class AuthenticatedAccount(BaseModel):
    """Who is making the request. Built by authentication; cart and orders depend on this shape."""

    model_config = ConfigDict(strict=True, frozen=True)

    id: EightCharId
    role: Role
    is_active: bool


class Session(BaseModel):
    """A signed-in session. Stores a SHA-256 of the token, never the token itself."""

    token_hash: NonEmptyText
    account_id: EightCharId
    created_at: AwareDatetime
    expires_at: AwareDatetime


class SignInRequest(BaseModel):
    email: LoginEmail
    password: SecretStr


class TokenResponse(BaseModel):
    """Returned by sign-in. The client sends `access_token` back as `Authorization: Bearer <token>`."""

    access_token: NonEmptyText
    token_type: Literal["bearer"] = "bearer"
    expires_at: AwareDatetime
