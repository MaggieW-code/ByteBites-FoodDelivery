from typing import Annotated

from pydantic import BaseModel, Field

# The one place the restaurant ID rule lives. Routes reuse it for path parameters.
# (Account IDs have their own EightCharId in account_model.py.)
RestaurantId = Annotated[str, Field(strict=True, min_length=8, max_length=8)]


class  Restaurant(BaseModel):
    id: RestaurantId
    name: str = Field(strict=True, min_length=1)
    cuisine: str = Field(strict=True, min_length=1)
    rating: float = Field(strict=True, ge=0, le=5)
    address: str = Field(strict=True, min_length=1)
    is_active: bool = Field(strict=True)
   
class CreateRestaurantRequest(BaseModel):
    name: str = Field(strict=True, min_length=1)
    cuisine: str = Field(strict=True, min_length=1)
    address: str = Field(strict=True, min_length=1)


class UpdateRestaurantRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, strict=True)
    cuisine: str | None = Field(default=None, min_length=1, strict=True)
    address: str | None = Field(default=None, min_length=1, strict=True)
