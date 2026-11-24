from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field

# Accepted price: a JSON number (14.99) or a decimal string ("14.99"),
# 0 or more (0 = free item), at most 2 decimal places, at most 999999.99.
# Anything else (more decimals, inf/nan, too large, not a number) is rejected with 422,
# so the saved price is always exactly the price that was sent.
Price = Annotated[
    Decimal,
    Field(ge=0, max_digits=8, decimal_places=2, allow_inf_nan=False),
]

class MenuListItem(BaseModel):
    id: str
    name: str
    description: str
    price: Decimal
    is_available: bool

class Menu(BaseModel):
    restaurant_id: str
    currency: str
    items: list[MenuListItem]

class CreateMenuItem(BaseModel):
    name: str = Field(strict = True, min_length = 1)
    category: str = Field(strict = True, min_length = 1)
    price: Price
    is_available: bool = Field(strict = True)
    description: str = Field(default="", strict=True)
    
# what the app saves and returns
class MenuItem(CreateMenuItem):
    id: str = Field(strict = True, min_length = 8, max_length = 8)
    restaurant_id: str = Field(strict = True, min_length=8, max_length = 8)

class UpdateMenuItem(BaseModel):
    name: str | None = Field(default = None, strict = True, min_length = 1)
    category: str | None = Field(default = None, strict = True, min_length = 1)
    price: Price | None = None
    is_available: bool | None = Field(default = None, strict = True)