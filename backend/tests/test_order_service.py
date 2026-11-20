from unittest.mock import Mock

import pytest

from backend.app.repositories.order_repository import OrderRepository
from backend.app.services.order_service import (
    OrderAccessDeniedError,
    OrderNotFoundError,
    OrderService,
)
from backend.tests.test_order_repository import make_order


def test_get_owned_order():
    repository = Mock(spec=OrderRepository)
    order = make_order()
    repository.get_by_id.return_value = order

    assert OrderService(repository).get_order(
        order.order_id, requester_id=order.customer_id
    ) == order
    repository.get_by_id.assert_called_once_with(order.order_id)


@pytest.mark.parametrize("order_exists", [False, True])
def test_missing_and_foreign_orders_are_indistinguishable(order_exists):
    repository = Mock(spec=OrderRepository)
    repository.get_by_id.return_value = make_order() if order_exists else None

    with pytest.raises(OrderNotFoundError):
        OrderService(repository).get_order("order_001", requester_id="other_customer")


def test_history_queries_only_the_requested_owner():
    repository = Mock(spec=OrderRepository)
    order = make_order()
    repository.get_by_customer_id.return_value = [order]

    assert OrderService(repository).get_customer_orders(
        order.customer_id, requester_id=order.customer_id
    ) == [order]
    repository.get_by_customer_id.assert_called_once_with(order.customer_id)


def test_foreign_history_is_rejected_before_reading_storage():
    repository = Mock(spec=OrderRepository)

    with pytest.raises(OrderAccessDeniedError):
        OrderService(repository).get_customer_orders("customer_002", requester_id="customer_001")

    repository.get_by_customer_id.assert_not_called()
