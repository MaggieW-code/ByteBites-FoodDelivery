from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi import Path as PathParameter
from fastapi.responses import JSONResponse

from backend.app.models.cart_model import AddCartItemRequest, CartResponse, UpdateCartItemRequest
from backend.app.repositories.cart_repository import CartRepository
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.services.cart_service import (
    CartItemNotFoundError,
    CartItemUnavailableError,
    CartMenuItemNotFoundError,
    CartRestaurantMismatchError,
    CartService,
    CartServiceError,
    CartValidationError,
)

router = APIRouter(prefix="/cart", tags=["cart"])
data_directory = Path(__file__).resolve().parents[1] / "data"
cart_service = CartService(
    CartRepository(data_directory / "carts.json"),
    MenuRepository(data_directory / "menus.json"),
)


def get_authenticated_customer_id(request: Request) -> str:
    """Read the customer ID set by authentication middleware after verification."""
    customer_id = getattr(request.state, "authenticated_customer_id", None)
    if not isinstance(customer_id, str) or not customer_id.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer authentication required",
        )
    return customer_id


def get_cart_service() -> CartService:
    return cart_service


async def handle_cart_service_error(_request: Request, error: CartServiceError) -> JSONResponse:
    detail = str(error)
    if isinstance(error, (CartItemNotFoundError, CartMenuItemNotFoundError)):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(error, (CartItemUnavailableError, CartRestaurantMismatchError)):
        code = status.HTTP_409_CONFLICT
    elif isinstance(error, CartValidationError):
        code = 422
    else:
        code = status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = "Unable to access cart data"
    return JSONResponse(status_code=code, content={"detail": detail})


CustomerId = Annotated[str, Depends(get_authenticated_customer_id)]
Service = Annotated[CartService, Depends(get_cart_service)]
ItemId = Annotated[str, PathParameter(min_length=8, max_length=8)]


@router.post("", response_model=CartResponse)
def get_or_create_cart(customer_id: CustomerId, service: Service) -> CartResponse:
    return service.get_or_create_cart(customer_id)


@router.get("", response_model=CartResponse)
def get_cart(customer_id: CustomerId, service: Service) -> CartResponse:
    return service.get_cart(customer_id)


@router.post("/items", response_model=CartResponse)
def add_item(
    data: AddCartItemRequest,
    restaurant_id: Annotated[str, Query(min_length=8, max_length=8)],
    customer_id: CustomerId,
    service: Service,
) -> CartResponse:
    return service.add_item(customer_id, restaurant_id, data.menu_item_id, data.quantity)


@router.patch("/items/{item_id}", response_model=CartResponse)
def update_item(
    item_id: ItemId, data: UpdateCartItemRequest, customer_id: CustomerId, service: Service
) -> CartResponse:
    return service.update_item_quantity(customer_id, item_id, data.quantity)


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_item(item_id: ItemId, customer_id: CustomerId, service: Service) -> CartResponse:
    return service.remove_item(customer_id, item_id)


@router.delete("", response_model=CartResponse)
def clear_cart(customer_id: CustomerId, service: Service) -> CartResponse:
    return service.clear_cart(customer_id)
