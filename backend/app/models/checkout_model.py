from pydantic import BaseModel, ConfigDict

from backend.app.models.order_model import OrderIdentifier


class CheckoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cart_id: OrderIdentifier
