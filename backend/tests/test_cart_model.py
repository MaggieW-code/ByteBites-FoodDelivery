
import json
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.app.models.cart_model import (
    AddCartItemRequest,
    Cart,
    CartItem,
    CartResponse,
    CartStatus,
    UpdateCartItemRequest,
)


def cart_data():
    return {
        "id": "cart_001",
        "customer_id": "cust_001",
        "restaurant_id": "rest_001",
        "items": [{"menu_item_id": "menu_001", "quantity": 2}],
        "status": "active",
    }


def test_cart_validates_nested_items_and_status():
    cart = Cart(**cart_data())
    assert cart.items == [
        CartItem(menu_item_id="menu_001", quantity=2)
    ]
    assert cart.status is CartStatus.ACTIVE


@pytest.mark.parametrize("field", ["id", "customer_id"])
def test_cart_requires_identifiers(field):
    data = cart_data()
    del data[field]
    with pytest.raises(ValidationError):
        Cart(**data)


@pytest.mark.parametrize("field", ["id", "customer_id"])
@pytest.mark.parametrize("value", ["", None, 123])
def test_cart_rejects_invalid_identifiers(field, value):
    data = cart_data()
    data[field] = value
    with pytest.raises(ValidationError):
        Cart(**data)


def test_cart_allows_missing_restaurant():
    data = cart_data()
    data.pop("restaurant_id")
    data["items"] = []

    cart = Cart(**data)

    assert cart.restaurant_id is None
    assert cart.items == []


@pytest.mark.parametrize("value", ["", "short", "toolongid", 123])
def test_cart_rejects_invalid_restaurant_id(value):
    data = cart_data()
    data["restaurant_id"] = value

    with pytest.raises(ValidationError):
        Cart(**data)


@pytest.mark.parametrize("field", ["menu_item_id", "quantity"])
def test_cart_item_requires_fields(field):
    data = {"menu_item_id": "menu_001", "quantity": 1}
    del data[field]

    with pytest.raises(ValidationError):
        CartItem(**data)


@pytest.mark.parametrize(
    "quantity",
    [0, -1, 1.5, 2.0, "2", True, None],
)
@pytest.mark.parametrize(
    "model",
    [CartItem, AddCartItemRequest, UpdateCartItemRequest],
)
def test_quantity_must_be_a_positive_integer(model, quantity):
    data = {"quantity": quantity}

    if model is not UpdateCartItemRequest:
        data["menu_item_id"] = "menu_001"

    with pytest.raises(ValidationError):
        model(**data)


def test_cart_validates_nested_quantities():
    data = cart_data()
    data["items"][0]["quantity"] = 0

    with pytest.raises(ValidationError):
        Cart(**data)


def test_cart_defaults_are_independent():
    first = Cart(id="cart_001", customer_id="cust_001")
    second = Cart(id="cart_002", customer_id="cust_001")

    first.items.append(
        CartItem(menu_item_id="menu_001", quantity=1)
    )

    assert second.items == []
    assert second.status is CartStatus.ACTIVE


@pytest.mark.parametrize("status", list(CartStatus))
def test_cart_json_persistence_round_trip(status):
    cart = Cart(**(cart_data() | {"status": status}))

    assert json.loads(
        cart.model_dump_json()
    )["status"] == status.value

    assert Cart.model_validate_json(
        cart.model_dump_json()
    ) == cart

    assert json.loads(
        json.dumps(cart.model_dump(mode="json"))
    ) == cart.model_dump(mode="json")


def test_cart_rejects_unknown_status():
    with pytest.raises(ValidationError):
        Cart(**(cart_data() | {"status": "unknown"}))


def test_operation_requests():
    add_request = AddCartItemRequest(
        menu_item_id="menu_001",
        quantity=2,
    )
    update_request = UpdateCartItemRequest(quantity=3)

    assert add_request.quantity == 2
    assert update_request.quantity == 3


def test_response_preserves_monetary_precision_in_json():
    response = CartResponse(
        **cart_data(),
        subtotal=Decimal("19.98"),
        total=Decimal("22.38"),
    )

    data = json.loads(response.model_dump_json())

    assert data["subtotal"] == "19.98"
    assert data["total"] == "22.38"

    assert CartResponse.model_validate_json(
        response.model_dump_json()
    ) == response


@pytest.mark.parametrize("field", ["subtotal", "total"])
@pytest.mark.parametrize("value", ["-0.01", "NaN", "Infinity"])
def test_response_rejects_invalid_amounts(field, value):
    data = cart_data() | {
        "subtotal": "0.00",
        "total": "0.00",
        field: value,
    }

    with pytest.raises(ValidationError):
        CartResponse(**data)


@pytest.mark.parametrize("field", ["subtotal", "total"])
def test_response_requires_amounts(field):
    data = cart_data() | {
        "subtotal": "0.00",
        "total": "0.00",
    }
    del data[field]

    with pytest.raises(ValidationError):
        CartResponse(**data)
