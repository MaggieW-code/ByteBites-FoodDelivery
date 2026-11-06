from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


Identifier = Annotated[str, Field(strict=True, min_length=1)]
EightCharID = Annotated[str, Field(strict=True, min_length=8, max_length=8)]
PositiveQuantity = Annotated[int, Field(strict=True, gt=0)]
Money = Annotated[Decimal, Field(ge=0, allow_inf_nan=False)]


class CartStatus(str, Enum):
    ACTIVE = "active"
    CHECKED_OUT = "checked_out"


class CartItem(BaseModel):
    menu_item_id: EightCharID
    quantity: PositiveQuantity


class Cart(BaseModel):
    id: Identifier
    customer_id: Identifier
    restaurant_id: EightCharID | None = None
    items: list[CartItem] = Field(default_factory=list)
    status: CartStatus = CartStatus.ACTIVE


class AddCartItemRequest(CartItem):
    pass


class UpdateCartItemRequest(BaseModel):
    quantity: PositiveQuantity


class CartResponse(Cart):
    subtotal: Money
    total: Money
