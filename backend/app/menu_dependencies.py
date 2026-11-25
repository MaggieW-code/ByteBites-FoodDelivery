from backend.app.config import get_data_file_path, get_restaurant_data_path
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services.menu_service import MenuService


def get_menu_service() -> MenuService:
    return MenuService(
        MenuRepository(get_data_file_path("MENUS_PATH", "menus.json")),
        RestaurantRepository(get_restaurant_data_path()),
    )


menu_service = get_menu_service()
