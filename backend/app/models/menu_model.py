from decimal import Decimal
from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator, Field

def _number_to_decimal(value: Any) -> Any:
    # 14.99 -> Decimal("14.99"); strings are left alone so strict rejects them
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return Decimal(str(value))
    return value

Price = Annotated[Decimal, BeforeValidator(_number_to_decimal), Field(strict=True, gt=0)]

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
    price: Price = Field(strict = True, gt = 0)
    is_available: bool = Field(strict = True)
    description: str = Field(default="", strict=True)
    
# what the app saves and returns
class MenuItem(CreateMenuItem):
    id: str = Field(strict = True, min_length = 8, max_length = 8)
    restaurant_id: str = Field(strict = True, min_length=8, max_length = 8)

class UpdateMenuItem(BaseModel):
    name: str | None = Field(default = None, strict = True, min_length = 1)
    category: str | None = Field(default = None, strict = True, min_length = 1)
    price: Price | None = Field(default = None, strict = True, gt = 0)
    is_available: bool | None = Field(default = None, strict = True)