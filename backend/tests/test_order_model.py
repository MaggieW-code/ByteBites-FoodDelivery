
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.app.models.order_model import Order, OrderItem


def make_item():
    return OrderItem(
        item_id="menu_001",
        name="Burger",
        quantity=2,
        unit_price=Decimal("12.50"),
        line_total=Decimal("25.00"),
    )


def make_order():
    return Order(
        order_id="order_001",
        customer_id="cust_001",
        restaurant_id="rest_001",
        items=[make_item()],
        total=Decimal("25.00"),
    )


def test_valid_order_item():
    item = make_item()

    assert item.quantity == 2
    assert item.unit_price == Decimal("12.50")
    assert item.line_total == Decimal("25.00")


def test_invalid_quantity():
    with pytest.raises(ValidationError):
        OrderItem(
            item_id="menu_001",
            name="Burger",
            quantity=0,
            unit_price=Decimal("12.50"),
            line_total=Decimal("0"),
        )


def test_invalid_price():
    with pytest.raises(ValidationError):
        OrderItem(
            item_id="menu_001",
            name="Burger",
            quantity=1,
            unit_price=Decimal("-5"),
            line_total=Decimal("0"),
        )


def test_incorrect_line_total():
    with pytest.raises(ValidationError):
        OrderItem(
            item_id="menu_001",
            name="Burger",
            quantity=2,
            unit_price=Decimal("12.50"),
            line_total=Decimal("10.00"),
        )


def test_valid_order():
    order = make_order()

    assert order.total == Decimal("25.00")
    assert order.status == "created"
    assert order.customer_id == "cust_001"


def test_incorrect_order_total():
    with pytest.raises(ValidationError):
        Order(
            order_id="order_001",
            customer_id="cust_001",
            restaurant_id="rest_001",
            items=[make_item()],
            total=Decimal("10.00"),
        )


def test_json_serialization():
    original = make_order()

    json_data = original.model_dump_json()
    restored = Order.model_validate_json(json_data)

    assert restored == original
    assert restored.total == Decimal("25.00")


def test_empty_order_items():
    with pytest.raises(ValidationError):
        Order(
            order_id="order_001",
            customer_id="cust_001",
            restaurant_id="rest_001",
            items=[],
            total=Decimal("0"),
        )


def test_missing_customer_id():
    with pytest.raises(ValidationError):
        Order(
            order_id="order_001",
            customer_id="",
            restaurant_id="rest_001",
            items=[make_item()],
            total=Decimal("25.00"),
        )
