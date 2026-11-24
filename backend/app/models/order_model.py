from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

OrderIdentifier = Annotated[str, Field(strict=True, min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")]
Money = Annotated[Decimal, Field(ge=0, decimal_places=2)]


class OrderItem(BaseModel):
    item_id: OrderIdentifier
    name: str = Field(min_length=1)
    quantity: int = Field(strict=True, gt=0)
    unit_price: Money
    line_total: Money

    @model_validator(mode="after")
    def validate_line_total(self):
        expected = self.unit_price * self.quantity

        if self.line_total != expected:
            raise ValueError("Incorrect line total")

        return self


class Order(BaseModel):
    order_id: OrderIdentifier
    customer_id: OrderIdentifier
    restaurant_id: OrderIdentifier

    items: list[OrderItem] = Field(min_length=1)
    total: Money

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
