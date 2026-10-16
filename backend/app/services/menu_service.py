from backend.app.models.menu_model import Menu
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository


class MenuRestaurantNotFoundError(Exception):
    pass


class MenuService:
    def __init__(self, menu_repository: MenuRepository, restaurant_repository: RestaurantRepository):
        self.menu_repository = menu_repository
        self.restaurant_repository = restaurant_repository

    def get_menu(self, restaurant_id: str) -> Menu:
        if self.restaurant_repository.get_by_id(restaurant_id) is None:
            raise MenuRestaurantNotFoundError(f"Restaurant '{restaurant_id}' not found")
        menu = self.menu_repository.get_by_restaurant_id(restaurant_id)
        if menu is None:
            return Menu(restaurant_id=restaurant_id, currency="CAD", items=[])
        return Menu(**menu)
