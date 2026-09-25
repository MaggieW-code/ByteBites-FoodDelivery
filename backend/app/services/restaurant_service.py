from backend.app.models.restaurant_model import Restaurant
from backend.app.repositories.restaurant_repository import RestaurantRepository


class RestaurantService:
    def __init__(self, repository: RestaurantRepository):
        self.repository = repository

    def get_restaurants(self) -> list[Restaurant]:
        data = self.repository.get_all()

        return [
            Restaurant(**restaurant) for restaurant in data
        ]
