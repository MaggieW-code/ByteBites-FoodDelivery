from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4

from pydantic import TypeAdapter, ValidationError

from backend.app.models.cart_model import Cart, CartItem, CartResponse, CartStatus, CheckoutCart, Money
from backend.app.models.menu_model import MenuItem
from backend.app.repositories.cart_repository import CartDataError, CartRepository
from backend.app.services.menu_service import (
    MenuReadError,
    MenuRestaurantInactiveError,
    MenuRestaurantNotFoundError,
    MenuService,
)


class CartServiceError(Exception):
    """Base error for cart operations."""


class CartValidationError(CartServiceError):
    pass


class CartItemNotFoundError(CartServiceError):
    pass


class CartMenuItemNotFoundError(CartServiceError):
    pass


class CartItemUnavailableError(CartServiceError):
    pass


class CartRestaurantMismatchError(CartServiceError):
    pass


class CartStorageError(CartServiceError):
    pass


@dataclass(frozen=True)
class CartCheckoutSession:
    cart: CheckoutCart | None
    _close_cart: Callable[[], None]

    def close_cart(self) -> None:
        self._close_cart()


class CartService:
    _price = TypeAdapter(Money)

    def __init__(self, cart_repository: CartRepository, menu_service: MenuService):
        self.cart_repository = cart_repository
        self.menu_service = menu_service

    def get_or_create_cart(self, customer_id: str) -> CartResponse:
        with self._operation():
            cart, exists = self._active_cart(customer_id)
            response = self._response(cart)

            if not exists:
                self._persist(cart, exists)

            return response

    def get_cart(self, customer_id: str) -> CartResponse:
        """Return the current cart, initializing an empty cart if needed."""
        return self.get_or_create_cart(customer_id)

    def add_item(
        self, customer_id: str, restaurant_id: str, menu_item_id: str, quantity: int
    ) -> CartResponse:
        self._validate_quantity(quantity)
        if not isinstance(restaurant_id, str) or len(restaurant_id) != 8:
            raise CartValidationError("Restaurant ID must be an eight-character string")
        try:
            item = CartItem(menu_item_id=menu_item_id, quantity=quantity)
        except ValidationError as error:
            raise CartValidationError("Invalid menu item ID") from error

        with self._operation():
            cart, exists = self._active_cart(customer_id)
            if cart.restaurant_id is not None and cart.restaurant_id != restaurant_id:
                raise CartRestaurantMismatchError("All cart items must be from the same restaurant")

            menu_items = self._menu_items(restaurant_id, require_active=True)
            if self._menu_item(menu_items, menu_item_id).is_available is False:
                raise CartItemUnavailableError(f"Menu item '{menu_item_id}' is unavailable")

            cart.restaurant_id = restaurant_id
            for index, existing in enumerate(cart.items):
                if existing.menu_item_id == menu_item_id:
                    try:
                        cart.items[index] = CartItem(
                            menu_item_id=menu_item_id,
                            quantity=existing.quantity + quantity,
                        )
                    except ValidationError as error:
                        raise CartValidationError(
                            "Invalid combined cart item quantity"
                        ) from error
                    break
            else:
                cart.items.append(item)

            response = self._response(cart, menu_items)
            self._persist(cart, exists)
            return response

    def update_item_quantity(
        self, customer_id: str, menu_item_id: str, quantity: int
    ) -> CartResponse:
        self._validate_quantity(quantity)
        with self._operation():
            cart, exists = self._active_cart(customer_id)
            cart.items[self._item_index(cart, menu_item_id)].quantity = quantity
            response = self._response(cart)
            self._persist(cart, exists)
            return response

    def remove_item(self, customer_id: str, menu_item_id: str) -> CartResponse:
        with self._operation():
            cart, exists = self._active_cart(customer_id)
            cart.items.pop(self._item_index(cart, menu_item_id))
            if not cart.items:
                cart.restaurant_id = None
            response = self._response(cart)
            self._persist(cart, exists)
            return response

    def clear_cart(self, customer_id: str) -> CartResponse:
        with self._operation():
            cart, exists = self._active_cart(customer_id)
            cart.items.clear()
            cart.restaurant_id = None
            self._persist(cart, exists)
            return self._response(cart)

    @contextmanager
    def checkout_session(self, customer_id: str, cart_id: str) -> Iterator[CartCheckoutSession]:
        """Hold the selected cart stable until checkout saves the order and closes it."""
        with self.cart_repository.locked():
            cart = self.cart_repository.get_active_by_customer_id(customer_id)
            if cart is not None and cart.id != cart_id:
                cart = None

            def close_cart() -> None:
                if cart is None:
                    raise CartStorageError("No active cart to close")
                self._persist(cart.model_copy(update={"status": CartStatus.CHECKED_OUT}), exists=True)

            snapshot = None
            if cart is not None:
                snapshot = CheckoutCart(
                    customer_id=cart.customer_id,
                    restaurant_id=cart.restaurant_id,
                    items=tuple((item.menu_item_id, item.quantity) for item in cart.items),
                )
            yield CartCheckoutSession(snapshot, close_cart)

    @contextmanager
    def _operation(self) -> Iterator[None]:
        try:
            with self.cart_repository.locked():
                yield
        except (CartDataError, OSError) as error:
            raise CartStorageError("Unable to access cart storage") from error

    def _active_cart(self, customer_id: str) -> tuple[Cart, bool]:
        if not isinstance(customer_id, str) or not customer_id:
            raise CartValidationError("Customer ID must be a nonempty string")
        cart = self.cart_repository.get_active_by_customer_id(customer_id)
        if cart is None:
            return Cart(id=uuid4().hex, customer_id=customer_id), False
        return cart, True

    def _persist(self, cart: Cart, exists: bool) -> None:
        if not exists:
            self.cart_repository.create(cart)
        elif self.cart_repository.update(cart) is None:
            raise CartStorageError(f"Cart '{cart.id}' disappeared before it could be saved")

    @staticmethod
    def _validate_quantity(quantity: int) -> None:
        if type(quantity) is not int or quantity <= 0:
            raise CartValidationError("Cart item quantity must be a positive integer")

    @staticmethod
    def _item_index(cart: Cart, menu_item_id: str) -> int:
        for index, item in enumerate(cart.items):
            if item.menu_item_id == menu_item_id:
                return index
        raise CartItemNotFoundError(f"Item '{menu_item_id}' is not in the cart")

    def _menu_items(
        self, restaurant_id: str, *, require_active: bool = False
    ) -> dict[str, MenuItem]:
        try:
            menu = self.menu_service.get_menu(restaurant_id, require_active=require_active)
        except MenuRestaurantNotFoundError:
            return {}
        except MenuRestaurantInactiveError as error:
            raise CartItemUnavailableError(str(error)) from error
        except MenuReadError as error:
            raise CartStorageError("Unable to read restaurant menu data") from error
        return {item.id: item for item in menu.items}

    @staticmethod
    def _menu_item(menu_items: dict[str, MenuItem], menu_item_id: str) -> MenuItem:
        try:
            return menu_items[menu_item_id]
        except KeyError as error:
            raise CartMenuItemNotFoundError(f"Menu item '{menu_item_id}' was not found") from error

    def _response(
        self, cart: Cart, menu_items: dict[str, MenuItem] | None = None
    ) -> CartResponse:
        subtotal = Decimal("0.00")
        if cart.items:
            if cart.restaurant_id is None:
                raise CartStorageError(f"Cart '{cart.id}' has items without a restaurant")
            if menu_items is None:
                menu_items = self._menu_items(cart.restaurant_id)

            for item in cart.items:
                menu_item = self._menu_item(menu_items, item.menu_item_id)
                try:
                    price = self._price.validate_python(menu_item.price)
                except ValidationError as error:
                    raise CartStorageError(
                        f"Invalid menu price for item '{item.menu_item_id}'"
                    ) from error
                subtotal += price * item.quantity

        return CartResponse(**cart.model_dump(), subtotal=subtotal, total=subtotal)
