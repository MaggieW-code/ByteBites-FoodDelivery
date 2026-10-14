from pathlib import Path
from fastapi import APIRouter, HTTPException


from backend.app.models.menu_Item_model import CreateMenuItem, MenuItem
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.services.menu_service import MenuItemNotFoundError, MenuService
from backend.app.models.update_menu_item_model import UpdateMenuItem


router = APIRouter()

menu_repository = MenuRepository(
    Path("backend/app/data/menu_items.json")
)

menu_service = MenuService(
    menu_repository
)

@router.post("/restaurants/{restaurant_id}/menu", response_model=MenuItem, status_code=201)
def add_menu(restaurant_id: str, data: CreateMenuItem) -> MenuItem:
    return menu_service.add_menu(restaurant_id, data)

@router.patch("/restaurants/{restaurant_id}/menu/{menu_item_id}", response_model=MenuItem)
def update_menu(restaurant_id: str, menu_item_id: str, data: UpdateMenuItem) -> MenuItem:
    try:
        return menu_service.update_menu(restaurant_id, menu_item_id, data)
    except MenuItemNotFoundError:
        raise HTTPException(status_code=404, detail="Menu item not found")
