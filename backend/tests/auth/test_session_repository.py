from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from backend.app.models.accounts.auth_model import Session
from backend.app.repositories.json_list_store import DataFileMalformedError
from backend.app.repositories.accounts.session_repository import SessionRepository


def make_session(token_hash: str = "hash_of_new_token", account_id: str = "ownr_001") -> Session:
    created_at = datetime(2026, 11, 22, 14, 0, tzinfo=timezone.utc)
    return Session(
        token_hash=token_hash,
        account_id=account_id,
        created_at=created_at,
        expires_at=created_at + timedelta(hours=1),
    )


def test_get_by_token_hash_finds_session(session_repository: SessionRepository) -> None:
    session = session_repository.get_by_token_hash("hash_of_cara_token")

    assert session is not None
    assert session.account_id == "cust_001"
    assert session.expires_at.tzinfo is not None


def test_get_by_token_hash_returns_none_when_missing(session_repository: SessionRepository) -> None:
    assert session_repository.get_by_token_hash("unknown") is None


def test_add_persists_with_timezone(session_repository: SessionRepository, sessions_file: Path) -> None:
    session_repository.add(make_session())

    reloaded = SessionRepository(sessions_file).get_by_token_hash("hash_of_new_token")

    assert reloaded == make_session()


def test_delete_removes_only_that_session(session_repository: SessionRepository, sessions_file: Path) -> None:
    session_repository.add(make_session())

    assert session_repository.delete_by_token_hash("hash_of_cara_token") is True

    reloaded = SessionRepository(sessions_file)
    assert reloaded.get_by_token_hash("hash_of_cara_token") is None
    assert reloaded.get_by_token_hash("hash_of_new_token") is not None


def test_delete_unknown_session_returns_false(session_repository: SessionRepository) -> None:
    assert session_repository.delete_by_token_hash("unknown") is False


def test_delete_by_account_removes_all_of_its_sessions_only(
    session_repository: SessionRepository, sessions_file: Path
) -> None:
    session_repository.add(make_session("hash_of_cara_phone", account_id="cust_001"))
    session_repository.add(make_session("hash_of_omar_token", account_id="ownr_001"))

    assert session_repository.delete_by_account_id("cust_001") == 2

    reloaded = SessionRepository(sessions_file)
    assert [session.token_hash for session in reloaded.load_all()] == ["hash_of_omar_token"]


def test_delete_by_account_without_sessions_returns_zero(session_repository: SessionRepository) -> None:
    assert session_repository.delete_by_account_id("nope_000") == 0


def test_missing_sessions_file_means_no_sessions(tmp_path: Path) -> None:
    sessions_file = tmp_path / "sessions.json"
    repository = SessionRepository(sessions_file)

    assert repository.get_by_token_hash("anything") is None

    repository.add(make_session())
    assert SessionRepository(sessions_file).get_by_token_hash("hash_of_new_token") == make_session()


def test_malformed_sessions_file_raises(tmp_path: Path) -> None:
    sessions_file = tmp_path / "sessions.json"
    sessions_file.write_text("[{]", encoding="utf-8")

    with pytest.raises(DataFileMalformedError):
        SessionRepository(sessions_file).get_by_token_hash("anything")
