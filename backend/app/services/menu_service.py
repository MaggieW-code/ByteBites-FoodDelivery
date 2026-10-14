import uuid

from backend.app.models.menu_Item_model import MenuItem, CreateMenuItem
from backend.app.repositories.menu_repository import MenuRepository


class MenuService:
    def __init__(self, repository: MenuRepository):
        self.repository = repository

    def add_menu(self, restaurant_id: str, data: CreateMenuItem) -> MenuItem:
        new_id = uuid.uuid4().hex[:8]

        item = MenuItem(
            id = new_id,
            restaurant_id = restaurant_id,
            name = data.name,
            category = data.category,
            price = data.price,
            is_available = data.is_available
        )
        self.repository.add(item)
        return item

    def get_menu(self) -> list[MenuItem]:
        menus = self.repository.get_all()

        return [
            MenuItem(**menu) for menu in menus
        ]