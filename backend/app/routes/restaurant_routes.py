from pathlib import Path
from fastapi import APIRouter, HTTPException, Path as PathParameter, Query, status

from backend.app.models.restaurant_model import (
    Restaurant,
    CreateRestaurantRequest,
    UpdateRestaurantRequest,
)
from backend.app.repositories.restaurant_repository import RestaurantRepository
from backend.app.services.restaurant_service import RestaurantNotFoundError, RestaurantService

router = APIRouter()

restaurant_repository = RestaurantRepository(
    Path("backend/app/data/restaurants.json")
)

restaurant_service = RestaurantService(
    restaurant_repository
)

@router.get(
    "/restaurants", response_model=list[Restaurant],
    description="List persisted restaurants, optionally filtered by cuisine. Matching is exact, case-insensitive, and ignores surrounding whitespace. No matches returns an empty list.",
)
def restaurants(
    cuisine: str | None = Query(default=None, description="Cuisine to match, e.g. Japanese. Omit or leave blank for all cuisines."),
) -> list[Restaurant]:
    return restaurant_service.get_restaurants(cuisine)


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


@router.post(
    "/restaurants",
    response_model=Restaurant,
    status_code=status.HTTP_201_CREATED,
)
def create_restaurant(
    request: CreateRestaurantRequest,
) -> Restaurant:
    return restaurant_service.create_restaurant(request)


@router.patch(
    "/restaurants/{restaurant_id}",
    response_model=Restaurant,
)
def update_restaurant(
    restaurant_id: str,
    request: UpdateRestaurantRequest,
) -> Restaurant:
    try:
        updated = restaurant_service.update_restaurant(
            restaurant_id,
            request,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error

    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )

    return updated
