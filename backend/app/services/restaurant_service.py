
from uuid import uuid4

from backend.app.models.restaurant_model import (
    Restaurant,
    CreateRestaurantRequest,
    UpdateRestaurantRequest,
)
from backend.app.repositories.restaurant_repository import RestaurantRepository


class RestaurantService:
    def __init__(self, repository: RestaurantRepository):
        self.repository = repository

    def get_restaurants(self) -> list[Restaurant]:
        data = self.repository.get_all()

        return [
            Restaurant(**restaurant) for restaurant in data
        ]


    
    def create_restaurant(
        self, request: CreateRestaurantRequest
    ) -> Restaurant:

        existing_ids = {
            restaurant["id"]
            for restaurant in self.repository.get_all()
        }

        restaurant_id = uuid4().hex[:8]

        while restaurant_id in existing_ids:
            restaurant_id = uuid4().hex[:8]

        restaurant = Restaurant(
            id=restaurant_id,
            name=request.name,
            cuisine=request.cuisine,
            address=request.address,
            rating=0.0,
            is_active=True,
        )

        saved = self.repository.create(restaurant.model_dump())

        return Restaurant(**saved)


    
    def update_restaurant(
        self,
        restaurant_id: str,
        request: UpdateRestaurantRequest,
    ) -> Restaurant | None:

        updates = request.model_dump(exclude_unset=True)

        if not updates:
            raise ValueError("At least one field must be provided")

        if any(value is None for value in updates.values()):
            raise ValueError("Restaurant fields cannot be null")

        updated = self.repository.update(
            restaurant_id,
            updates,
        )

        if updated is None:
            return None

        return Restaurant(**updated)

