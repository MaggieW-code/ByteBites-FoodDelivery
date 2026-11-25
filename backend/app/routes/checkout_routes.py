from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.dependencies.commerce import get_checkout_service
from backend.app.models.checkout_model import CheckoutRequest
from backend.app.models.order_model import Order
from backend.app.routes.auth_dependencies import CurrentCustomer
from backend.app.services.checkout_service import (
    CheckoutCartNotFoundError,
    CheckoutConflictError,
    CheckoutService,
    CheckoutUnavailableError,
)

router = APIRouter(tags=["checkout"])


@router.post(
    "/checkout",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    summary="Check out the signed-in customer's cart",
    description="Price the selected cart from the current menu, persist an order, and close the cart.",
    responses={
        401: {"description": "Missing, invalid, or expired credentials"},
        403: {"description": "An active customer account is required"},
        404: {"description": "The selected cart is not visible to the customer"},
        409: {"description": "The cart or its items cannot be checked out"},
    },
)
def checkout(
    data: CheckoutRequest,
    customer: CurrentCustomer,
    service: Annotated[CheckoutService, Depends(get_checkout_service)],
) -> Order:
    try:
        return service.checkout(customer_id=customer.customer_id, cart_id=data.cart_id)
    except CheckoutCartNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
    except (CheckoutConflictError, CheckoutUnavailableError) as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from error
