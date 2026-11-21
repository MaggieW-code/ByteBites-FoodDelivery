
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock

from pydantic import ValidationError

from backend.app.models.cart_model import Cart, CartStatus


class CartDataError(Exception):
    """The cart store contains invalid records or conflicting IDs."""


class CartDataMalformedError(CartDataError):
    """The cart store cannot be decoded as JSON."""


class CartRepository:
    _write_lock = Lock()

    def __init__(self, data_path: Path):
        self.data_path = Path(data_path)

    def get_all(self) -> list[Cart]:
        try:
            with self.data_path.open("r", encoding="utf-8") as file:
                records = json.load(file)
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise CartDataMalformedError(
                f"Cart data is malformed: {self.data_path}"
            ) from error

        if not isinstance(records, list):
            raise CartDataError(
                f"Cart data must contain a list: {self.data_path}"
            )

        try:
            carts = [Cart.model_validate(record) for record in records]
        except ValidationError as error:
            raise CartDataError(
                f"Invalid cart record: {self.data_path}"
            ) from error

        if len({cart.id for cart in carts}) != len(carts):
            raise CartDataError(
                f"Duplicate cart IDs: {self.data_path}"
            )

        return carts

    def get_by_id(self, cart_id: str) -> Cart | None:
        return next(
            (cart for cart in self.get_all() if cart.id == cart_id),
            None,
        )

    def get_active_by_customer_id(
        self, customer_id: str
    ) -> Cart | None:
        return next(
            (
                cart
                for cart in self.get_all()
                if cart.customer_id == customer_id
                and cart.status == CartStatus.ACTIVE
            ),
            None,
        )

    def _check_active_cart(
        self, cart: Cart, carts: list[Cart]
    ) -> None:
        if cart.status == CartStatus.ACTIVE and any(
            existing.customer_id == cart.customer_id
            and existing.status == CartStatus.ACTIVE
            and existing.id != cart.id
            for existing in carts
        ):
            raise CartDataError(
                f"Customer already has an active cart: {cart.customer_id}"
            )

    def create(self, cart: Cart) -> Cart:
        with self._write_lock:
            carts = self.get_all()

            if any(existing.id == cart.id for existing in carts):
                raise CartDataError(
                    f"Cart already exists: {cart.id}"
                )

            self._check_active_cart(cart, carts)
            carts.append(cart)
            self._save(carts)

        return cart

    def update(self, cart: Cart) -> Cart | None:
        with self._write_lock:
            carts = self.get_all()

            for index, existing in enumerate(carts):
                if existing.id == cart.id:
                    self._check_active_cart(cart, carts)
                    carts[index] = cart
                    self._save(carts)
                    return cart

        return None

    def _save(self, carts: list[Cart]) -> None:
        records = [
            cart.model_dump(mode="json")
            for cart in carts
        ]

        temporary_path = None

        try:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.data_path.parent,
                delete=False,
            ) as file:
                temporary_path = Path(file.name)
                json.dump(records, file, indent=2)

            temporary_path.replace(self.data_path)

        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
