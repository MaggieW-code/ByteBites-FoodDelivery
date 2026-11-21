from pathlib import Path

from backend.app.repositories.menu_repository import MenuRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services.menu_service import MenuService

data_directory = Path(__file__).resolve().parent / "data"
menu_service = MenuService(
    MenuRepository(data_directory / "menus.json"),
    RestaurantRepository(data_directory / "restaurants.json"),
)
