from pathlib import Path

from fastapi import APIRouter, HTTPException, Path as PathParameter

from backend.app.models.menu_model import Menu
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services.menu_service import MenuRestaurantNotFoundError, MenuService

router = APIRouter()
data_directory = Path(__file__).resolve().parents[1] / "data"
menu_service = MenuService(
    MenuRepository(data_directory / "menus.json"),
    RestaurantRepository(data_directory / "restaurants.json"),
)


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
