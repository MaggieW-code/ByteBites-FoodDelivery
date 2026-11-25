from backend.app.models.order_model import Order
from backend.app.repositories.order_repository import OrderRepository


class OrderNotFoundError(Exception):
    """No order with the given ID is visible to the customer."""


class OrderAccessDeniedError(Exception):
    """The requested order history belongs to another customer."""


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def get_order(self, order_id: str, *, requester_id: str) -> Order:
        order = self.repository.get_by_id(order_id)
        if order is None or order.customer_id != requester_id:
            raise OrderNotFoundError
        return order

    def get_customer_orders(self, customer_id: str, *, requester_id: str) -> list[Order]:
        if customer_id != requester_id:
            raise OrderAccessDeniedError
        return self.repository.get_by_customer_id(customer_id)
