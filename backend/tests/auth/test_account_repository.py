from pathlib import Path

import pytest

from backend.app.models.account_model import StoredCustomerAccount, StoredRestaurantAccount
from backend.app.repositories.account_repository import AccountRepository
from backend.app.repositories.json_list_store import DataFileMalformedError, DataFileMissingError


def make_customer(account_id: str = "cust_009", email: str = "new@example.com") -> StoredCustomerAccount:
    return StoredCustomerAccount(
        id=account_id,
        full_name="New Customer",
        email=email,
        phone="250-555-0199",
        is_active=True,
        password_hash="scrypt$salt$hash",
    )


def test_get_by_id_returns_stored_class_for_role(account_repository: AccountRepository) -> None:
    owner = account_repository.get_by_id("ownr_001")

    assert type(owner) is StoredRestaurantAccount
    assert owner.password_hash == "scrypt$salt$hash"


def test_get_by_id_returns_none_when_missing(account_repository: AccountRepository) -> None:
    assert account_repository.get_by_id("nope_000") is None


@pytest.mark.parametrize("email", ["cara@example.com", "  CARA@Example.com "])
def test_get_by_email_ignores_case_and_spaces(account_repository: AccountRepository, email: str) -> None:
    account = account_repository.get_by_email(email)

    assert account is not None
    assert account.id == "cust_001"


def test_get_by_email_returns_none_when_missing(account_repository: AccountRepository) -> None:
    assert account_repository.get_by_email("ghost@example.com") is None


def test_add_persists_across_a_new_repository(account_repository: AccountRepository, accounts_file: Path) -> None:
    account_repository.add(make_customer())

    reloaded = AccountRepository(accounts_file).get_by_id("cust_009")

    assert reloaded == make_customer()


def test_ids_stay_stable_after_writes(account_repository: AccountRepository, accounts_file: Path) -> None:
    ids_before = ["cust_001", "cust_002", "ownr_001"]

    account_repository.add(make_customer())
    reloaded = AccountRepository(accounts_file)

    assert all(reloaded.get_by_id(account_id) is not None for account_id in ids_before)


def test_update_replaces_the_matching_account(account_repository: AccountRepository, accounts_file: Path) -> None:
    cara = account_repository.get_by_id("cust_001")
    deactivated = cara.model_copy(update={"is_active": False})

    assert account_repository.update(deactivated) == deactivated
    assert AccountRepository(accounts_file).get_by_id("cust_001").is_active is False
    assert AccountRepository(accounts_file).get_by_id("ownr_001").is_active is True


def test_update_returns_none_for_unknown_account(account_repository: AccountRepository) -> None:
    assert account_repository.update(make_customer(account_id="nope_000")) is None


def test_missing_accounts_file_raises(tmp_path: Path) -> None:
    with pytest.raises(DataFileMissingError):
        AccountRepository(tmp_path / "accounts.json").get_by_id("cust_001")


@pytest.mark.parametrize(
    "contents",
    ["not json", '{"id": "cust_001"}', '[{"id": "cust_001", "role": "chef"}]'],
    ids=["invalid-json", "not-a-list", "invalid-record"],
)
def test_malformed_accounts_file_raises(tmp_path: Path, contents: str) -> None:
    accounts_file = tmp_path / "accounts.json"
    accounts_file.write_text(contents, encoding="utf-8")

    with pytest.raises(DataFileMalformedError):
        AccountRepository(accounts_file).get_by_id("cust_001")
