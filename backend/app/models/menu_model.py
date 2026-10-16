from decimal import Decimal

from pydantic import BaseModel


class MenuItem(BaseModel):
    id: str
    name: str
    description: str
    price: Decimal
    is_available: bool


class Menu(BaseModel):
    restaurant_id: str
    currency: str
    items: list[MenuItem]
