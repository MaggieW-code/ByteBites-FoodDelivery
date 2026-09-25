from pathlib import Path

from fastapi import APIRouter

from backend.app.models.restaurant_model import Restaurant
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services.restaurant_service import RestaurantService

router = APIRouter()

restaurant_repository = RestaurantRepository(
    Path("backend/app/data/restaurants.json")
)

restaurant_service = RestaurantService(
    restaurant_repository
)

@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/restaurants", response_model=list[Restaurant])
def restaurants() -> list[Restaurant]:
    return restaurant_service.get_restaurants()

