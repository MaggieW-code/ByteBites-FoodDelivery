import json
from decimal import Decimal

import pytest

from backend.app.models.cart_model import CartStatus
from backend.app.repositories.cart_repository import CartRepository
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services.cart_service import (
    CartItemNotFoundError,
    CartItemUnavailableError,
    CartMenuItemNotFoundError,
    CartRestaurantMismatchError,
    CartService,
    CartStorageError,
    CartValidationError,
)
from backend.app.services.menu_service import MenuService


@pytest.fixture
def service(tmp_path):
    restaurant_path = tmp_path / "restaurants.json"
    restaurant_path.write_text(
        json.dumps(
            [
                {"id": "rest_001", "is_active": True},
                {"id": "rest_002", "is_active": True},
            ]
        ),
        encoding="utf-8",
    )
    menu_path = tmp_path / "menus.json"
    menu_path.write_text(
        json.dumps(
            [
                {
                    "restaurant_id": "rest_001",
                    "currency": "CAD",
                    "items": [
                        {"id": "item_001", "name": "item_001", "description": "", "price": "0.10", "is_available": True},
                        {"id": "item_002", "name": "item_002", "description": "", "price": 2.35, "is_available": True},
                        {"id": "item_003", "name": "item_003", "description": "", "price": "1.00", "is_available": False},
                    ],
                },
                {
                    "restaurant_id": "rest_002",
                    "currency": "CAD",
                    "items": [
                        {"id": "item_004", "name": "item_004", "description": "", "price": "4.25", "is_available": True}
                    ],
                },
            ]
        ),
        encoding="utf-8",
    )

    return CartService(
        CartRepository(tmp_path / "carts.json"),
        MenuService(MenuRepository(menu_path), RestaurantRepository(restaurant_path)),
    )


def test_get_or_create_cart(service):
    first = service.get_or_create_cart("customer")

    assert service.get_cart("customer") == first
    assert service.get_cart("other").id != first.id

    stored = service.cart_repository.get_by_id(first.id)
    stored.status = CartStatus.CHECKED_OUT
    service.cart_repository.update(stored)

    active = service.get_or_create_cart("customer")

    assert active.id != first.id
    assert active.status == CartStatus.ACTIVE


def test_add_update_and_persist_cart(service):
    first = service.add_item("customer", "rest_001", "item_001", 1)
    assert first.total == Decimal("0.10")

    service.add_item("customer", "rest_001", "item_002", 2)
    merged = service.add_item("customer", "rest_001", "item_001", 2)

    assert [(item.menu_item_id, item.quantity) for item in merged.items] == [
        ("item_001", 3),
        ("item_002", 2),
    ]
    assert merged.subtotal == merged.total == Decimal("5.00")

    updated = service.update_item_quantity("customer", "item_002", 1)
    assert updated.total == Decimal("2.65")

    reopened = CartService(
        CartRepository(service.cart_repository.data_path),
        service.menu_service,
    )
    assert reopened.get_cart("customer") == updated


def test_totals_use_current_menu_prices(service, tmp_path):
    cart = service.add_item("customer", "rest_001", "item_001", 3)

    menu_path = tmp_path / "menus.json"
    menus = json.loads(menu_path.read_text(encoding="utf-8"))
    menus[0]["items"][0]["price"] = "0.20"
    menu_path.write_text(json.dumps(menus), encoding="utf-8")

    repriced = service.get_cart("customer")

    assert repriced.id == cart.id
    assert repriced.subtotal == repriced.total == Decimal("0.60")


def test_remove_and_clear_cart(service):
    initial = service.add_item("customer", "rest_001", "item_001", 2)
    service.add_item("customer", "rest_001", "item_002", 1)

    remaining = service.remove_item("customer", "item_001")
    assert remaining.restaurant_id == "rest_001"
    assert remaining.total == Decimal("2.35")

    empty = service.remove_item("customer", "item_002")
    assert empty.items == []
    assert empty.restaurant_id is None
    assert empty.total == Decimal("0.00")

    service.add_item("customer", "rest_002", "item_004", 1)
    cleared = service.clear_cart("customer")

    assert cleared == empty
    assert cleared.id == initial.id
    assert service.clear_cart("customer") == cleared


def test_empty_cart_without_menu_data(service, tmp_path):
    (tmp_path / "menus.json").unlink()

    cart = service.clear_cart("customer")

    assert cart.items == []
    assert cart.restaurant_id is None
    assert cart.subtotal == cart.total == Decimal("0.00")


@pytest.mark.parametrize("quantity", [0, -1, 1.5, True, "2"])
def test_invalid_quantities(service, quantity):
    initial = service.add_item("customer", "rest_001", "item_001", 2)

    with pytest.raises(CartValidationError):
        service.add_item("customer", "rest_001", "item_001", quantity)

    with pytest.raises(CartValidationError):
        service.update_item_quantity("customer", "item_001", quantity)

    assert service.get_cart("customer") == initial


def test_missing_cart_item(service):
    with pytest.raises(CartItemNotFoundError):
        service.remove_item("customer", "item_001")

    with pytest.raises(CartItemNotFoundError):
        service.update_item_quantity("customer", "item_001", 1)

    assert service.cart_repository.get_all() == []

    initial = service.add_item("customer", "rest_001", "item_001", 2)

    with pytest.raises(CartItemNotFoundError):
        service.remove_item("customer", "item_002")

    assert service.get_cart("customer") == initial


def test_reject_invalid_menu_items_and_restaurants(service):
    initial = service.add_item("customer", "rest_001", "item_001", 1)

    with pytest.raises(CartMenuItemNotFoundError):
        service.add_item("customer", "rest_001", "item_999", 1)

    with pytest.raises(CartItemUnavailableError):
        service.add_item("customer", "rest_001", "item_003", 1)

    with pytest.raises(CartRestaurantMismatchError):
        service.add_item("customer", "rest_002", "item_004", 1)

    assert service.get_cart("customer") == initial


def test_invalid_backend_price_preserves_cart(service, tmp_path):
    initial = service.add_item("customer", "rest_001", "item_001", 1)

    menu_path = tmp_path / "menus.json"
    menus = json.loads(menu_path.read_text(encoding="utf-8"))
    menus[0]["items"][1]["price"] = "-1.00"
    menu_path.write_text(json.dumps(menus), encoding="utf-8")

    with pytest.raises(CartStorageError, match="Invalid menu price"):
        service.add_item("customer", "rest_001", "item_002", 1)

    assert service.get_cart("customer") == initial


def test_failed_update_preserves_stored_cart(service, tmp_path):
    initial = service.add_item("customer", "rest_001", "item_001", 2)

    menu_path = tmp_path / "menus.json"
    menus = json.loads(menu_path.read_text(encoding="utf-8"))
    menus[0]["items"][0]["price"] = "-1.00"
    menu_path.write_text(json.dumps(menus), encoding="utf-8")

    with pytest.raises(CartStorageError):
        service.update_item_quantity("customer", "item_001", 5)

    stored = service.cart_repository.get_by_id(initial.id)
    assert stored.items[0].quantity == 2


def test_malformed_cart_storage(service):
    service.cart_repository.data_path.write_text("{", encoding="utf-8")

    with pytest.raises(CartStorageError):
        service.get_cart("customer")


@pytest.mark.parametrize("customer_id", ["", None, 123, []])
def test_invalid_customer_id(service, customer_id):
    with pytest.raises(CartValidationError):
        service.get_or_create_cart(customer_id)

    assert service.cart_repository.get_all() == []


@pytest.mark.parametrize(
    "restaurant_id",
    ["", "short", "restaurant_001", None, 123],
)
def test_invalid_restaurant_id(service, restaurant_id):
    with pytest.raises(CartValidationError):
        service.add_item("customer", restaurant_id, "item_001", 1)

    assert service.cart_repository.get_all() == []


def test_checkout_session_only_exposes_selected_customer_cart(service):
    cart = service.add_item("customer", "rest_001", "item_001", 2)

    with service.checkout_session("other", cart.id) as session:
        assert session.cart is None
    with service.checkout_session("customer", "other-cart") as session:
        assert session.cart is None

    assert service.cart_repository.get_by_id(cart.id).status == CartStatus.ACTIVE


def test_checkout_session_holds_snapshot_until_order_save(service):
    cart = service.add_item("customer", "rest_001", "item_001", 2)

    with service.checkout_session("customer", cart.id) as session:
        assert session.cart.customer_id == "customer"
        assert session.cart.restaurant_id == "rest_001"
        assert session.cart.items == (("item_001", 2),)
        assert service.cart_repository.get_by_id(cart.id).status == CartStatus.ACTIVE
    assert service.cart_repository.get_by_id(cart.id).status == CartStatus.ACTIVE

    with service.checkout_session("customer", cart.id) as session:
        session.close_cart()

    assert service.cart_repository.get_by_id(cart.id).status == CartStatus.CHECKED_OUT
    assert service.get_cart("customer").id != cart.id
