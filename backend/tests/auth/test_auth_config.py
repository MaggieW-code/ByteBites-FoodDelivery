from datetime import timedelta
from pathlib import Path

import pytest

from backend.app.config import get_accounts_data_path, get_auth_token_lifetime, get_sessions_data_path


@pytest.mark.parametrize(
    "getter, variable, default_name",
    [(get_accounts_data_path, "ACCOUNTS_PATH", "accounts.json"), (get_sessions_data_path, "SESSIONS_PATH", "sessions.json")],
    ids=["accounts", "sessions"],
)
def test_data_paths_default_and_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, getter, variable: str, default_name: str
) -> None:
    monkeypatch.delenv(variable, raising=False)
    assert getter().name == default_name
    assert getter().parent.name == "data"

    monkeypatch.setenv(variable, str(tmp_path / "custom.json"))
    assert getter() == tmp_path / "custom.json"


def test_token_lifetime_defaults_to_an_hour(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AUTH_TOKEN_TTL_MINUTES", raising=False)

    assert get_auth_token_lifetime() == timedelta(minutes=60)


def test_token_lifetime_reads_minutes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH_TOKEN_TTL_MINUTES", "15")

    assert get_auth_token_lifetime() == timedelta(minutes=15)


@pytest.mark.parametrize("value", ["0", "-5", "ten", ""])
def test_token_lifetime_rejects_bad_values(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("AUTH_TOKEN_TTL_MINUTES", value)

    with pytest.raises(ValueError, match="AUTH_TOKEN_TTL_MINUTES"):
        get_auth_token_lifetime()
