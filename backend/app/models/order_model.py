
from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class OrderItem(BaseModel):
    item_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    quantity: int = Field(strict=True, gt=0)
    unit_price: Decimal = Field(gt=0)
    line_total: Decimal = Field(ge=0)

    @model_validator(mode="after")
    def validate_line_total(self):
        expected = self.unit_price * self.quantity

        if self.line_total != expected:
            raise ValueError("Incorrect line total")

        return self


class Order(BaseModel):
    order_id: str = Field(min_length=1)
    customer_id: str = Field(min_length=1)
    restaurant_id: str = Field(min_length=1)

    items: list[OrderItem] = Field(min_length=1)
    total: Decimal = Field(ge=0)

    status: Literal["created"] = "created"

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @model_validator(mode="after")
    def validate_total(self):
        expected = sum(
            (item.line_total for item in self.items),
            Decimal("0")
        )

        if self.total != expected:
            raise ValueError("Incorrect order total")

        return self
