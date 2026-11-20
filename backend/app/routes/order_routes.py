from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.models.order_model import Order
from backend.app.repositories.order_repository import OrderRepository
from backend.app.services.order_service import (
    OrderAccessDeniedError,
    OrderNotFoundError,
    OrderService,
)

router = APIRouter(tags=["orders"])
order_service = OrderService(
    OrderRepository(Path(__file__).resolve().parents[1] / "data" / "orders.json")
)


def get_authenticated_order_customer_id() -> str:
    """Resolve a verified active customer once the shared auth dependency is available."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Customer authentication required",
    )


def get_order_service() -> OrderService:
    return order_service


CustomerId = Annotated[str, Depends(get_authenticated_order_customer_id)]
Service = Annotated[OrderService, Depends(get_order_service)]


@router.get(
    "/orders/{order_id}",
    response_model=Order,
    summary="Get an order placed by the signed-in customer",
    responses={
        401: {"description": "Customer authentication required"},
        403: {"description": "An active customer account is required"},
        404: {"description": "No order with that ID is visible to the customer"},
    },
)
def get_order(order_id: str, requester_id: CustomerId, service: Service) -> Order:
    try:
        return service.get_order(order_id, requester_id=requester_id)
    except OrderNotFoundError as error:
        raise HTTPException(status_code=404, detail="Order not found") from error


@router.get(
    "/customers/{customer_id}/orders",
    response_model=list[Order],
    summary="List the signed-in customer's orders",
    description="Returns purchase-time order details. An empty history returns an empty list.",
    responses={
        401: {"description": "Customer authentication required"},
        403: {"description": "Access to the requested customer history is forbidden"},
    },
)
def get_customer_orders(
    customer_id: str, requester_id: CustomerId, service: Service
) -> list[Order]:
    try:
        return service.get_customer_orders(customer_id, requester_id=requester_id)
    except OrderAccessDeniedError as error:
        raise HTTPException(status_code=403, detail="Order history access denied") from error
