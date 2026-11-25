import json
import os
import tempfile
from pathlib import Path

from filelock import FileLock
from pydantic import ValidationError

from backend.app.models.order_model import Order


class OrderDataError(Exception):
    """Order storage contains invalid data."""


class OrderDataMalformedError(OrderDataError):
    """Order storage cannot be parsed as valid UTF-8 JSON."""


class DuplicateOrderError(OrderDataError):
    """An order with the same ID already exists."""


class OrderRepository:
    def __init__(self, data_path: Path):
        self.data_path = Path(data_path)

    def get_all(self) -> list[Order]:
        try:
            with self.data_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise OrderDataMalformedError("Order storage contains malformed JSON") from error

        if not isinstance(data, list):
            raise OrderDataError("Order storage must contain a list")

        try:
            return [Order.model_validate(record) for record in data]
        except ValidationError as error:
            raise OrderDataError("Order storage contains an invalid order") from error

    def get_by_id(self, order_id: str) -> Order | None:
        for order in self.get_all():
            if order.order_id == order_id:
                return order

        return None

    def get_by_customer_id(self, customer_id: str) -> list[Order]:
        return [order for order in self.get_all() if order.customer_id == customer_id]

    def save(self, order: Order) -> Order:
        record = order.model_dump(mode="json")
        try:
            snapshot = Order.model_validate(record)
        except ValidationError as error:
            raise OrderDataError("Cannot save an invalid order") from error

        path = self.data_path.resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        # Lock a separate file so replacing the data file cannot invalidate the lock.
        with FileLock(path.with_name(path.name + ".lock"), timeout=10):
            orders = self.get_all()
            if any(existing.order_id == snapshot.order_id for existing in orders):
                raise DuplicateOrderError(f"Order '{snapshot.order_id}' already exists")
            serialized = [existing.model_dump(mode="json") for existing in orders]
            serialized.append(snapshot.model_dump(mode="json"))
            self._write(path, serialized)
        return snapshot

    def _write(self, path: Path, records: list[dict]) -> None:
        temporary_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                prefix=".orders_",
                suffix=".tmp",
                delete=False,
            ) as file:
                temporary_path = Path(file.name)
                json.dump(records, file, indent=2)

            os.replace(temporary_path, path)

        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
