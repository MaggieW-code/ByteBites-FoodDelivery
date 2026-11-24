from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from backend.app.dependencies.orders import get_order_service
from backend.app.models.order_model import Order
from backend.app.routes.auth_dependencies import CurrentCustomer
from backend.app.services.order_service import (
    OrderAccessDeniedError,
    OrderNotFoundError,
    OrderService,
)

router = APIRouter(tags=["orders"])
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
def get_order(order_id: str, customer: CurrentCustomer, service: Service) -> Order:
    try:
        return service.get_order(order_id, requester_id=customer.customer_id)
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
def get_customer_orders(customer_id: str, customer: CurrentCustomer, service: Service) -> list[Order]:
    try:
        return service.get_customer_orders(customer_id, requester_id=customer.customer_id)
    except OrderAccessDeniedError as error:
        raise HTTPException(status_code=403, detail="Order history access denied") from error
