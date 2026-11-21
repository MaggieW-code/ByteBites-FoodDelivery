from fastapi import APIRouter, HTTPException, Path as PathParameter

from backend.app.menu_dependencies import menu_service
from backend.app.models.menu_item_model import CreateMenuItem, MenuItem
from backend.app.models.menu_model import Menu
from backend.app.models.update_menu_item_model import UpdateMenuItem
from backend.app.services.menu_service import (
    MenuItemNotFoundError,
    MenuRestaurantNotFoundError,
)

router = APIRouter()


@router.get(
    "/restaurants/{restaurant_id}/menu",
    response_model=Menu,
    description="Retrieve a restaurant's persisted menu and items. Existing restaurants without items return an empty menu. Prices are decimal strings in the menu currency.",
    responses={404: {"description": "Restaurant not found"}},
)
def restaurant_menu(
    restaurant_id: str = PathParameter(..., min_length=8, max_length=8,
                                       description="Restaurant ID, for example rest_001"),
) -> Menu:
    try:
        return menu_service.get_menu(restaurant_id)
    except MenuRestaurantNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/restaurants/{restaurant_id}/menu", response_model=MenuItem, status_code=201)
def add_menu(restaurant_id: str, data: CreateMenuItem) -> MenuItem:
    return menu_service.add_menu(restaurant_id, data)


@router.patch("/restaurants/{restaurant_id}/menu/{menu_item_id}", response_model=MenuItem)
def update_menu(restaurant_id: str, menu_item_id: str, data: UpdateMenuItem) -> MenuItem:
    try:
        return menu_service.update_menu(restaurant_id, menu_item_id, data)
    except MenuItemNotFoundError:
        raise HTTPException(status_code=404, detail="Menu item not found")