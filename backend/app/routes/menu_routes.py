from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi import Path as PathParameter

from backend.app.models.menu_model import CreateMenuItem, Menu, MenuItem, MenuItemId, UpdateMenuItem
from backend.app.models.restaurant_model import RestaurantId
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services.menu_service import (
    MenuItemNotFoundError,
    MenuRestaurantNotFoundError,
    MenuService,
)

router = APIRouter()

# Use Annotated[...] so the ID rule from the model is applied to the path.
# (Writing `restaurant_id: RestaurantId = PathParameter(...)` would silently drop the rule.)
RestaurantIdPath = Annotated[RestaurantId, PathParameter(description="Restaurant ID, for example rest_001")]
MenuItemIdPath = Annotated[MenuItemId, PathParameter(description="Menu item ID, for example item_001")]
data_directory = Path(__file__).resolve().parents[1] / "data"
menu_service = MenuService(
    MenuRepository(data_directory / "menus.json"),
    RestaurantRepository(data_directory / "restaurants.json"),
)


@router.get(
    "/restaurants/{restaurant_id}/menu",
    response_model=Menu,
    description=(
        "Retrieve a restaurant's persisted menu and items. Existing restaurants without items "
        "return an empty menu. Prices are decimal strings in the menu currency."
    ),
    responses={404: {"description": "Restaurant not found"}},
)
def restaurant_menu(
    restaurant_id: RestaurantIdPath,
) -> Menu:
    try:
        return menu_service.get_menu(restaurant_id)
    except MenuRestaurantNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post(
    "/restaurants/{restaurant_id}/menu",
    response_model=MenuItem,
    status_code=201,
    responses={404: {"description": "Restaurant not found"}},
)
def add_menu(
    data: CreateMenuItem,
    restaurant_id: RestaurantIdPath,
) -> MenuItem:
    try:
        return menu_service.add_menu(restaurant_id, data)
    except MenuRestaurantNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.patch("/restaurants/{restaurant_id}/menu/{menu_item_id}", response_model=MenuItem)
def update_menu(
    restaurant_id: RestaurantIdPath,
    menu_item_id: MenuItemIdPath,
    data: UpdateMenuItem,
) -> MenuItem:
    try:
        return menu_service.update_menu(restaurant_id, menu_item_id, data)
    except MenuItemNotFoundError:
        raise HTTPException(status_code=404, detail="Menu item not found")