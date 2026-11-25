from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from backend.app.models.accounts.auth_model import Session
from backend.app.repositories.json_list_store import DataFileMalformedError, JsonListStore

sessions_adapter = TypeAdapter(list[Session])


class SessionRepository:
    """Sessions are runtime data: a missing file means nobody is signed in."""

    def __init__(self, data_path: Path) -> None:
        self.store = JsonListStore(data_path, is_missing_file_empty=True)

    def get_by_token_hash(self, token_hash: str) -> Session | None:
        return next((session for session in self.load_all() if session.token_hash == token_hash), None)

    def add(self, session: Session) -> Session:
        sessions = self.load_all()
        sessions.append(session)
        self.save_all(sessions)
        return session

    def delete_by_token_hash(self, token_hash: str) -> bool:
        sessions = self.load_all()
        remaining = [session for session in sessions if session.token_hash != token_hash]
        if len(remaining) == len(sessions):
            return False
        self.save_all(remaining)
        return True

    def delete_by_account_id(self, account_id: str) -> int:
        """Sign an account out everywhere. Returns how many sessions were removed."""
        sessions = self.load_all()
        remaining = [session for session in sessions if session.account_id != account_id]
        removed_count = len(sessions) - len(remaining)
        if removed_count:
            self.save_all(remaining)
        return removed_count

    def load_all(self) -> list[Session]:
        try:
            return sessions_adapter.validate_python(self.store.load())
        except ValidationError as error:
            raise DataFileMalformedError(f"Invalid session record in {self.store.data_path}") from error

    def save_all(self, sessions: list[Session]) -> None:
        self.store.save(sessions_adapter.dump_python(sessions, mode="json"))
