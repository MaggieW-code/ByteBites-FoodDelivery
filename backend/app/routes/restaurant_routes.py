from pathlib import Path

from fastapi import APIRouter, HTTPException, Path as PathParameter

from backend.app.models.restaurant_model import Restaurant
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services.restaurant_service import RestaurantNotFoundError, RestaurantService

router = APIRouter()

restaurant_repository = RestaurantRepository(
    Path("backend/app/data/restaurants.json")
)

restaurant_service = RestaurantService(
    restaurant_repository
)

@router.get("/restaurants", response_model=list[Restaurant])
def restaurants() -> list[Restaurant]:
    return restaurant_service.get_restaurants()


@router.get(
    "/restaurants/{restaurant_id}",
    response_model=Restaurant,
    summary="Get restaurant details",
    description="Retrieve a restaurant by its unique ID.",
    responses={
        404: {"description": "Restaurant not found"}
    },
)
def restaurant_details(
    restaurant_id: str = PathParameter(
        ...,
        min_length=8,
        max_length=8,
        description="Restaurant ID, e.g. rest_001",
    ),
) -> Restaurant:
    try:
        return restaurant_service.get_restaurant_by_id(
            restaurant_id
        )

    except RestaurantNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
