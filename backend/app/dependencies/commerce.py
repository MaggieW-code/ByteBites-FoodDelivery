from typing import Annotated

from fastapi import Depends

from backend.app.config import get_data_file_path, get_restaurant_data_path
from backend.app.dependencies.orders import get_order_repository
from backend.app.menu_dependencies import get_menu_service
from backend.app.repositories.cart_repository import CartRepository
from backend.app.repositories.order_repository import OrderRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services.cart_service import CartService
from backend.app.services.checkout_service import CheckoutService
from backend.app.services.menu_service import MenuService


def get_cart_service(menus: Annotated[MenuService, Depends(get_menu_service)]) -> CartService:
    return CartService(CartRepository(get_data_file_path("CARTS_PATH", "carts.json")), menus)


def get_checkout_service(
    carts: Annotated[CartService, Depends(get_cart_service)],
    menus: Annotated[MenuService, Depends(get_menu_service)],
    orders: Annotated[OrderRepository, Depends(get_order_repository)],
) -> CheckoutService:
    return CheckoutService(carts, RestaurantRepository(get_restaurant_data_path()), menus, orders)
