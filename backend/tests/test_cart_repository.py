import json

import pytest

from backend.app.models.cart_model import Cart, CartItem, CartStatus
from backend.app.repositories.cart_repository import (
    CartDataError,
    CartDataMalformedError,
    CartRepository,
)


@pytest.fixture
def repository(tmp_path):
    return CartRepository(tmp_path / "carts.json")


def test_create_and_retrieve_active_cart(repository):
    checked_out = Cart(id="old", customer_id="customer", status=CartStatus.CHECKED_OUT)
    cart = Cart(id="new", customer_id="customer")
    repository.create(checked_out)

    assert repository.create(cart) == cart
    assert repository.get_by_id(cart.id) == cart
    assert repository.get_by_id(checked_out.id) == checked_out
    assert repository.get_active_by_customer_id(cart.customer_id) == cart
    assert repository.get_active_by_customer_id("someone-else") is None


def test_update_persists_across_repository_instances(repository):
    repository.create(Cart(id="cart", customer_id="customer"))
    updated = Cart(
        id="cart",
        customer_id="customer",
        restaurant_id="rest0001",
        items=[CartItem(menu_item_id="item0001", quantity=3)],
        status=CartStatus.CHECKED_OUT,
    )

    assert repository.update(updated) == updated
    assert json.loads(repository.data_path.read_text(encoding="utf-8")) == [
        {
            "id": "cart",
            "customer_id": "customer",
            "restaurant_id": "rest0001",
            "items": [{"menu_item_id": "item0001", "quantity": 3}],
            "status": "checked_out",
        }
    ]

    reopened = CartRepository(repository.data_path)
    assert reopened.get_by_id(updated.id) == updated
    assert reopened.get_active_by_customer_id(updated.customer_id) is None


def test_missing_cart(repository):
    assert repository.get_by_id("missing") is None
    assert repository.get_active_by_customer_id("missing") is None
    assert repository.update(Cart(id="missing", customer_id="customer")) is None
    assert not repository.data_path.exists()


def test_update_replaces_active_cart_and_preserves_other_customers(repository):
    cart = Cart(id="cart", customer_id="customer")
    other = Cart(id="other", customer_id="someone-else")
    updated = Cart(id=cart.id, customer_id=cart.customer_id, restaurant_id="rest0001")

    repository.create(cart)
    repository.create(other)
    assert repository.update(updated) == updated
    assert repository.get_all() == [updated, other]
    assert repository.get_active_by_customer_id(cart.customer_id) == updated


def test_create_rejects_duplicate_cart_id(repository):
    cart = Cart(id="cart", customer_id="customer")
    repository.create(cart)

    duplicate = Cart(id=cart.id, customer_id="someone-else")
    with pytest.raises(CartDataError, match="already exists"):
        repository.create(duplicate)

    assert repository.get_all() == [cart]


def test_create_rejects_second_active_cart_until_checkout(repository):
    cart = Cart(id="first", customer_id="customer")
    next_cart = Cart(id="second", customer_id=cart.customer_id)
    repository.create(cart)

    with pytest.raises(CartDataError, match="already has an active cart"):
        repository.create(next_cart)

    assert repository.get_all() == [cart]

    checked_out = cart.model_copy(update={"status": CartStatus.CHECKED_OUT})
    repository.update(checked_out)

    assert repository.create(next_cart) == next_cart
    assert repository.get_active_by_customer_id(cart.customer_id) == next_cart


def test_update_rejects_reactivating_cart_when_customer_has_an_active_cart(repository):
    checked_out = Cart(id="old", customer_id="customer", status=CartStatus.CHECKED_OUT)
    active = Cart(id="new", customer_id=checked_out.customer_id)
    repository.create(checked_out)
    repository.create(active)

    reactivated = checked_out.model_copy(update={"status": CartStatus.ACTIVE})
    with pytest.raises(CartDataError, match="already has an active cart"):
        repository.update(reactivated)

    assert repository.get_all() == [checked_out, active]


@pytest.mark.parametrize(
    ("contents", "error"),
    [
        ("{", CartDataMalformedError),
        ("{}", CartDataError),
        ('[{"id": "cart"}]', CartDataError),
        (
            '[{"id": "cart", "customer_id": "customer", '
            '"items": [{"menu_item_id": "item0001", "quantity": 0}]}]',
            CartDataError,
        ),
    ],
)
def test_malformed_data_is_reported_without_overwriting_file(repository, contents, error):
    repository.data_path.write_text(contents, encoding="utf-8")

    with pytest.raises(error):
        repository.get_by_id("cart")
    cart = Cart(id="cart", customer_id="customer")
    with pytest.raises(error):
        repository.create(cart)
    with pytest.raises(error):
        repository.update(cart)

    assert repository.data_path.read_text(encoding="utf-8") == contents
