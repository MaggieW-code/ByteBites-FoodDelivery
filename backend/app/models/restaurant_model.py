from pydantic import BaseModel, Field


class  Restaurant(BaseModel):
    id: str = Field(strict=True, min_length=8, max_length=8)
    name: str = Field(strict=True, min_length=1)
    cuisine: str = Field(strict=True, min_length=1)
    rating: float = Field(strict=True, ge=0, le=5)
    address: str = Field(strict=True, min_length=1)
    is_active: bool = Field(strict=True)