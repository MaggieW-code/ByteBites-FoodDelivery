import uuid

from backend.app.models.menu_item_model import CreateMenuItem, MenuItem
from backend.app.models.menu_model import Menu
from backend.app.models.update_menu_item_model import UpdateMenuItem
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.repositories.restaurant_repository import RestaurantRepository


class MenuRestaurantNotFoundError(Exception):
    pass


class MenuItemNotFoundError(Exception):
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

    def add_menu(self, restaurant_id: str, data: CreateMenuItem) -> MenuItem:
        item = MenuItem(
            id=uuid.uuid4().hex[:8],
            restaurant_id=restaurant_id,
            name=data.name,
            category=data.category,
            price=data.price,
            is_available=data.is_available,
            description=data.description,
        )
        self.menu_repository.add(item)
        return item

    def update_menu(self, restaurant_id: str, menu_item_id: str, data: UpdateMenuItem) -> MenuItem:
        record = self.menu_repository.find_item(restaurant_id, menu_item_id)
        if record is None:
            raise MenuItemNotFoundError("Menu item not found for this restaurant")

        item = MenuItem(**{
            "category": "uncategorized",
            **record,
            "price": float(record["price"]),
            "restaurant_id": restaurant_id,
        })
        updated = item.model_copy(update=data.model_dump(exclude_none=True))
        self.menu_repository.update(updated)
        return updated