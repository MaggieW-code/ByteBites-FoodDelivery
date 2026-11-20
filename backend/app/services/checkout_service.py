from contextlib import AbstractContextManager
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import NAMESPACE_URL, uuid5

from pydantic import ValidationError

from backend.app.models.order_model import Order, OrderItem
from backend.app.repositories.order_repository import OrderRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services.menu_service import MenuService


class CheckoutUnavailableError(Exception):
    """The requested cart, restaurant, or menu item cannot be checked out."""


class CheckoutConflictError(Exception):
    """The cart is invalid or has changed since its order was saved."""


@dataclass(frozen=True)
class CheckoutCart:
    customer_id: str
    restaurant_id: str | None
    items: tuple[tuple[str, int], ...]


class CheckoutSession(Protocol):
    @property
    def cart(self) -> CheckoutCart | None: ...

    def close_cart(self) -> None:
        """Close the exact cart held by this session."""
        ...


class CheckoutCarts(Protocol):
    def checkout_session(
        self, customer_id: str, cart_id: str
    ) -> AbstractContextManager[CheckoutSession]:
        """Hold the selected active cart stable through order save and closure."""
        ...


class CheckoutService:
    def __init__(
        self,
        carts: CheckoutCarts,
        restaurants: RestaurantRepository,
        menus: MenuService,
        orders: OrderRepository,
    ):
        self.carts = carts
        self.restaurants = restaurants
        self.menus = menus
        self.orders = orders

    def checkout(self, *, customer_id: str, cart_id: str) -> Order:
        """Check out a cart for the verified customer supplied by the caller."""
        if not customer_id.strip() or not cart_id.strip():
            raise CheckoutConflictError("Customer and cart IDs are required")

        # A stable ID makes retries after a failed cart close reuse the saved order.
        order_key = f"bytebites:checkout:{len(customer_id)}:{customer_id}:{cart_id}"
        order_id = uuid5(NAMESPACE_URL, order_key).hex
        with self.carts.checkout_session(customer_id, cart_id) as session:
            cart = session.cart
            if cart is not None and cart.customer_id != customer_id:
                raise CheckoutUnavailableError("Cart not found")

            existing = self.orders.get_by_id(order_id)
            if existing is not None:
                if existing.customer_id != customer_id:
                    raise CheckoutUnavailableError("Cart not found")
                if cart is not None:
                    purchased_items = {item.item_id: item.quantity for item in existing.items}
                    if (
                        cart.restaurant_id != existing.restaurant_id
                        or self._quantities(cart) != purchased_items
                    ):
                        raise CheckoutConflictError("Cart changed after its order was saved")
                    session.close_cart()
                return existing

            if cart is None:
                raise CheckoutUnavailableError("Cart not found")

            order = self._create_order(order_id, cart)
            saved = self.orders.save(order)
            session.close_cart()
            return saved

    @staticmethod
    def _quantities(cart: CheckoutCart) -> dict[str, int]:
        quantities = dict(cart.items)
        if (
            not quantities
            or len(quantities) != len(cart.items)
            or any(type(quantity) is not int or quantity <= 0 for quantity in quantities.values())
        ):
            raise CheckoutConflictError("Cart must contain distinct items with positive quantities")
        return quantities

    def _create_order(self, order_id: str, cart: CheckoutCart) -> Order:
        quantities = self._quantities(cart)
        restaurant_id = cart.restaurant_id
        if restaurant_id is None:
            raise CheckoutConflictError("Cart has no restaurant")
        restaurant = self.restaurants.get_by_id(restaurant_id)
        if restaurant is None or restaurant.get("is_active") is not True:
            raise CheckoutUnavailableError("Restaurant is unavailable")

        try:
            menu = self.menus.get_menu(restaurant_id)
        except ValidationError as error:
            raise CheckoutUnavailableError("Restaurant menu is invalid") from error
        menu_items = {item.id: item for item in menu.items}
        if menu.restaurant_id != restaurant_id or len(menu_items) != len(menu.items):
            raise CheckoutUnavailableError("Restaurant menu is invalid")

        items = []
        for item_id, quantity in quantities.items():
            item = menu_items.get(item_id)
            if item is None or not item.is_available:
                raise CheckoutUnavailableError(f"Menu item '{item_id}' is unavailable")
            if not item.price.is_finite() or item.price < 0 or not item.name.strip():
                raise CheckoutUnavailableError(f"Menu item '{item_id}' has invalid purchase details")
            items.append(
                OrderItem(
                    item_id=item.id,
                    name=item.name,
                    quantity=quantity,
                    unit_price=item.price,
                    line_total=item.price * quantity,
                )
            )
        return Order(
            order_id=order_id,
            customer_id=cart.customer_id,
            restaurant_id=restaurant_id,
            items=items,
            total=sum((item.line_total for item in items), Decimal("0")),
        )
