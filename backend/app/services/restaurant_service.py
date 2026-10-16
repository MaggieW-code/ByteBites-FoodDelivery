from backend.app.models.restaurant_model import Restaurant
from backend.app.repositories.restaurant_repository import RestaurantRepository


class RestaurantNotFoundError(Exception):
    """The requested restaurant does not exist."""


class RestaurantService:
    def __init__(self, repository: RestaurantRepository):
        self.repository = repository

    def get_restaurants(self) -> list[Restaurant]:
        data = self.repository.get_all()

        return [
            Restaurant(**restaurant) for restaurant in data
        ]

    def get_restaurant_by_id(self, restaurant_id: str) -> Restaurant:
        record = self.repository.get_by_id(restaurant_id)
        if record is None:
            raise RestaurantNotFoundError(f"Restaurant '{restaurant_id}' not found")
        return Restaurant(**record)
