from typing import Annotated

from fastapi import Depends

from backend.app.config import get_data_file_path
from backend.app.repositories.order_repository import OrderRepository
from backend.app.services.order_service import OrderService


def get_order_repository() -> OrderRepository:
    return OrderRepository(get_data_file_path("ORDERS_PATH", "orders.json"))


def get_order_service(orders: Annotated[OrderRepository, Depends(get_order_repository)]) -> OrderService:
    return OrderService(orders)
