from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from backend.app.models.accounts.account_model import StoredAccount
from backend.app.repositories.json_list_store import DataFileMalformedError, JsonListStore

stored_accounts_adapter = TypeAdapter(list[StoredAccount])


class AccountRepository:
    def __init__(self, data_path: Path) -> None:
        self.store = JsonListStore(data_path)

    def get_by_id(self, account_id: str) -> StoredAccount | None:
        return next((account for account in self.load_all() if account.id == account_id), None)

    def get_by_email(self, email: str) -> StoredAccount | None:
        normalized_email = email.strip().lower()
        return next((account for account in self.load_all() if account.email == normalized_email), None)

    def add(self, account: StoredAccount) -> StoredAccount:
        accounts = self.load_all()
        accounts.append(account)
        self.save_all(accounts)
        return account

    def update(self, account: StoredAccount) -> StoredAccount | None:
        accounts = self.load_all()
        for index, existing in enumerate(accounts):
            if existing.id == account.id:
                accounts[index] = account
                self.save_all(accounts)
                return account
        return None

    def load_all(self) -> list[StoredAccount]:
        try:
            return stored_accounts_adapter.validate_python(self.store.load())
        except ValidationError as error:
            raise DataFileMalformedError(f"Invalid account record in {self.store.data_path}") from error

    def save_all(self, accounts: list[StoredAccount]) -> None:
        self.store.save(stored_accounts_adapter.dump_python(accounts, mode="json"))
