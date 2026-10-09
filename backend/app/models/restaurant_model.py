from pydantic import BaseModel, Field


class  Restaurant(BaseModel):
    id: str = Field(strict=True, min_length=8, max_length=8)
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
