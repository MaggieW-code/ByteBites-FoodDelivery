
import json
import os
import tempfile
from pathlib import Path

from pydantic import ValidationError

from backend.app.models.order_model import Order


class OrderDataError(Exception):
    """Order storage contains invalid data."""


class OrderDataMalformedError(OrderDataError):
    """Order storage cannot be parsed as valid JSON."""


class DuplicateOrderError(OrderDataError):
    """An order with the same ID already exists."""


class OrderRepository:
    def __init__(self, data_path: Path):
        self.data_path = Path(data_path)

    def get_all(self) -> list[Order]:
        if not self.data_path.exists():
            return []

        try:
            with self.data_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise OrderDataMalformedError(
                "Order storage contains malformed JSON"
            ) from error

        if not isinstance(data, list):
            raise OrderDataError(
                "Order storage must contain a list"
            )

        try:
            return [Order.model_validate(record) for record in data]
        except ValidationError as error:
            raise OrderDataError(
                "Order storage contains an invalid order"
            ) from error

    def get_by_id(self, order_id: str) -> Order | None:
        for order in self.get_all():
            if order.order_id == order_id:
                return order

        return None

    def get_by_customer_id(self, customer_id: str) -> list[Order]:
        return [
            order
            for order in self.get_all()
            if order.customer_id == customer_id
        ]

    def save(self, order: Order) -> Order:
        orders = self.get_all()

        if any(existing.order_id == order.order_id for existing in orders):
            raise DuplicateOrderError(
                f"Order '{order.order_id}' already exists"
            )

        orders.append(order)

        serialized = [
            item.model_dump(mode="json")
            for item in orders
        ]

        self.data_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.data_path.parent,
                prefix=".orders_",
                suffix=".tmp",
                delete=False,
            ) as file:
                temporary_path = Path(file.name)
                json.dump(serialized, file, indent=2)

            os.replace(temporary_path, self.data_path)

        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

        return order
