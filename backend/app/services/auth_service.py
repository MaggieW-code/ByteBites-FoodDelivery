import hashlib
import secrets
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from functools import cache
from uuid import uuid4

from pydantic import TypeAdapter

from backend.app.models.account_model import (
    Account,
    AccountCreationRequest,
    Role,
    StoredAccount,
)
from backend.app.models.auth_model import AuthenticatedAccount, Session, SignInRequest, TokenResponse
from backend.app.repositories.account_repository import AccountRepository
from backend.app.repositories.session_repository import SessionRepository
from backend.app.services.password_hashing import hash_password, verify_password

account_adapter = TypeAdapter(Account)
stored_account_adapter = TypeAdapter(StoredAccount)


class AuthError(Exception):
    pass


class InvalidCredentialsError(AuthError):
    pass


class AccountDeactivatedError(AuthError):
    pass


class InvalidTokenError(AuthError):
    pass


class SessionExpiredError(AuthError):
    pass


class EmailAlreadyRegisteredError(AuthError):
    pass


class AccountNotFoundError(AuthError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@cache
def dummy_password_hash() -> str:
    """Checked against when the email is unknown, so both failures take the same time."""
    return hash_password(secrets.token_urlsafe(16))


class AuthService:
    def __init__(
        self,
        account_repository: AccountRepository,
        session_repository: SessionRepository,
        *,
        token_lifetime: timedelta,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self.account_repository = account_repository
        self.session_repository = session_repository
        self.token_lifetime = token_lifetime
        self.clock = clock

    def sign_in(self, request: SignInRequest) -> TokenResponse:
        account = self.account_repository.get_by_email(request.email)
        password = request.password.get_secret_value()
        if account is None:
            verify_password(password, dummy_password_hash())
            raise InvalidCredentialsError("Invalid email or password")
        if not verify_password(password, account.password_hash):
            raise InvalidCredentialsError("Invalid email or password")
        if not account.is_active:
            raise AccountDeactivatedError("Account is deactivated")

        token = secrets.token_urlsafe(32)
        now = self.clock()
        session = Session(
            token_hash=hash_token(token),
            account_id=account.id,
            created_at=now,
            expires_at=now + self.token_lifetime,
        )
        self.session_repository.add(session)
        return TokenResponse(access_token=token, expires_at=session.expires_at)

    def resolve_token(self, token: str) -> AuthenticatedAccount:
        token_hash = hash_token(token)
        session = self.session_repository.get_by_token_hash(token_hash)
        if session is None:
            raise InvalidTokenError("Invalid or signed-out token")
        if self.clock() >= session.expires_at:
            self.session_repository.delete_by_token_hash(token_hash)
            raise SessionExpiredError("Token has expired; sign in again")

        account = self.account_repository.get_by_id(session.account_id)
        if account is None:
            raise InvalidTokenError("Invalid or signed-out token")
        if not account.is_active:
            raise AccountDeactivatedError("Account is deactivated")
        return AuthenticatedAccount(id=account.id, role=account.role, is_active=account.is_active)

    def sign_out(self, token: str) -> None:
        self.session_repository.delete_by_token_hash(hash_token(token))

    def register_account(self, request: AccountCreationRequest, role: Role = "customer") -> Account:
        if self.account_repository.get_by_email(request.email) is not None:
            raise EmailAlreadyRegisteredError(f"Email already registered: {request.email}")

        stored = stored_account_adapter.validate_python(
            dict(
                id=self.new_account_id(),
                full_name=request.full_name,
                email=request.email,
                phone=request.phone,
                is_active=True,
                role=role,
                password_hash=hash_password(request.password.get_secret_value()),
            )
        )
        self.account_repository.add(stored)
        return to_public(stored)

    def get_account(self, account_id: str) -> Account:
        return to_public(self.get_stored_account(account_id))

    def deactivate_account(self, account_id: str) -> Account:
        stored = self.get_stored_account(account_id).model_copy(update={"is_active": False})
        self.account_repository.update(stored)
        return to_public(stored)

    def get_stored_account(self, account_id: str) -> StoredAccount:
        account = self.account_repository.get_by_id(account_id)
        if account is None:
            raise AccountNotFoundError(f"Account '{account_id}' not found")
        return account

    def new_account_id(self) -> str:
        account_id = uuid4().hex[:8]
        while self.account_repository.get_by_id(account_id) is not None:
            account_id = uuid4().hex[:8]
        return account_id


def to_public(stored: StoredAccount) -> Account:
    return account_adapter.validate_python(stored.model_dump())
