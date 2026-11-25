from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, SecretStr

from backend.app.models.account_model import EightCharId, Email, NonEmptyText, Role


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
    email: Email
    password: SecretStr


class TokenResponse(BaseModel):
    """Returned by sign-in. The client sends `access_token` back as `Authorization: Bearer <token>`."""

    access_token: NonEmptyText
    token_type: Literal["bearer"] = "bearer"
    expires_at: AwareDatetime
