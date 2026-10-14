from pathlib import Path
from fastapi import APIRouter

from backend.app.models.menu_Item_model import CreateMenuItem, MenuItem
from backend.app.repositories.menu_repository import MenuRepository
from backend.app.services.menu_service import MenuService

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