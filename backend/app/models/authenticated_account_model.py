from pydantic import BaseModel, ConfigDict, Field


class AuthenticatedAccount(BaseModel):
    """Trusted account data supplied by authentication after credential verification."""

    model_config = ConfigDict(strict=True, frozen=True)

    id: str = Field(min_length=1)
    role: str
    is_active: bool
