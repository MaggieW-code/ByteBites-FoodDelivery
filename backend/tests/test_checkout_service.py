from contextlib import nullcontext
from dataclasses import replace
from decimal import Decimal
from unittest.mock import Mock

import pytest

from backend.app.models.menu_model import Menu, MenuListItem
from backend.app.repositories.order_repository import OrderRepository
from backend.app.services.checkout_service import (
    CheckoutCart,
    CheckoutCartNotFoundError,
    CheckoutCarts,
    CheckoutConflictError,
    CheckoutService,
    CheckoutSession,
    CheckoutUnavailableError,
)
from backend.app.services.menu_service import (
    MenuRestaurantInactiveError,
    MenuRestaurantNotFoundError,
    MenuService,
)


@pytest.fixture
def checkout(tmp_path):
    session = Mock(spec=CheckoutSession)
    session.cart = CheckoutCart("customer_001", "rest_001", (("item_001", 2),))
    carts = Mock(spec=CheckoutCarts)
    carts.checkout_session.return_value = nullcontext(session)
    menus = Mock(spec=MenuService)
    menus.get_menu.return_value = Menu(
        restaurant_id="rest_001",
        currency="CAD",
        items=[
            MenuListItem(
                id="item_001",
                name="Burger",
                description="",
                price=Decimal("13.75"),
                is_available=True,
            )
        ],
    )
    orders = OrderRepository(tmp_path / "orders.json")
    return CheckoutService(carts, menus, orders), session


def place_order(service, cart_id="cart_001"):
    return service.checkout(customer_id="customer_001", cart_id=cart_id)


def test_checkout_prices_current_menu_and_persists_before_closing(checkout):
    service, session = checkout
    session.cart = replace(session.cart, items=(("item_001", 2), ("item_002", 1)))
    service.menus.get_menu.return_value.items.append(
        MenuListItem(id="item_002", name="Free sample", description="", price="0", is_available=True)
    )
    session.close_cart.side_effect = lambda: assert_order_persisted(service.orders)

    order = place_order(service)

    service.carts.checkout_session.assert_called_once_with("customer_001", "cart_001")
    session.close_cart.assert_called_once_with()
    assert order.total == Decimal("27.50")
    assert order.items[0].name == "Burger"
    assert order.items[0].quantity == 2
    assert order.items[0].unit_price == Decimal("13.75")
    assert order.items[1].line_total == Decimal("0")
    service.menus.get_menu.return_value.items[0].price = Decimal("20.00")
    assert service.orders.get_by_id(order.order_id) == order


def assert_order_persisted(repository):
    assert len(repository.get_all()) == 1


@pytest.mark.parametrize(
    "changes",
    [
        {"items": ()},
        {"items": (("item_001", 0),)},
        {"items": (("item_001", True),)},
        {"items": (("item_001", 1), ("item_001", 2))},
        {"restaurant_id": None},
    ],
)
def test_invalid_cart_does_not_create_order_or_close(checkout, changes):
    service, session = checkout
    session.cart = replace(session.cart, **changes)

    with pytest.raises(CheckoutConflictError):
        place_order(service)

    assert service.orders.get_all() == []
    session.close_cart.assert_not_called()


@pytest.mark.parametrize("customer_id", [None, "another_customer"])
def test_missing_or_foreign_cart_is_rejected(checkout, customer_id):
    service, session = checkout
    session.cart = None if customer_id is None else replace(session.cart, customer_id=customer_id)

    with pytest.raises(CheckoutCartNotFoundError, match="Cart not found"):
        place_order(service)

    assert service.orders.get_all() == []
    session.close_cart.assert_not_called()


@pytest.mark.parametrize("error", [MenuRestaurantNotFoundError("gone"), MenuRestaurantInactiveError("closed")])
def test_missing_or_inactive_restaurant_is_rejected(checkout, error):
    service, session = checkout
    service.menus.get_menu.side_effect = error

    with pytest.raises(CheckoutUnavailableError, match="Restaurant is unavailable"):
        place_order(service)

    assert service.orders.get_all() == []
    session.close_cart.assert_not_called()


@pytest.mark.parametrize("problem", ["missing", "unavailable", "negative_price", "fractional_cent_price"])
def test_invalid_menu_item_leaves_cart_open(checkout, problem):
    service, session = checkout
    menu = service.menus.get_menu.return_value
    if problem == "missing":
        menu.items.clear()
    elif problem == "unavailable":
        menu.items[0].is_available = False
    elif problem == "negative_price":
        menu.items[0].price = Decimal("-1")
    else:
        menu.items[0].price = Decimal("13.751")

    with pytest.raises(CheckoutUnavailableError):
        place_order(service)

    assert service.orders.get_all() == []
    session.close_cart.assert_not_called()


def test_failed_order_persistence_leaves_cart_open(checkout, monkeypatch):
    service, session = checkout
    save = Mock(side_effect=OSError("disk unavailable"))
    monkeypatch.setattr(service.orders, "save", save)

    with pytest.raises(OSError, match="disk unavailable"):
        place_order(service)

    assert service.orders.get_all() == []
    session.close_cart.assert_not_called()


def test_retries_reuse_order_after_cart_close_failure_or_success(checkout):
    service, session = checkout
    session.close_cart.side_effect = [OSError("cart unavailable"), None]

    with pytest.raises(OSError, match="cart unavailable"):
        place_order(service)

    (saved,) = service.orders.get_all()
    service.menus.get_menu.return_value.items[0].price = Decimal("20.00")
    assert place_order(service) == saved
    session.cart = None
    assert place_order(service) == saved
    assert service.orders.get_all() == [saved]
    assert session.close_cart.call_count == 2


def test_retry_does_not_close_a_cart_changed_since_persistence(checkout):
    service, session = checkout
    session.close_cart.side_effect = OSError("cart unavailable")
    with pytest.raises(OSError):
        place_order(service)
    (saved,) = service.orders.get_all()
    session.close_cart.reset_mock()
    session.cart = replace(session.cart, items=(("item_001", 3),))

    with pytest.raises(CheckoutConflictError, match="Cart changed"):
        place_order(service)

    assert service.orders.get_all() == [saved]
    session.close_cart.assert_not_called()


def test_checkout_asks_the_menu_feature_for_an_active_restaurant(checkout):
    service, _ = checkout

    place_order(service)

    service.menus.get_menu.assert_called_once_with("rest_001", require_active=True)
