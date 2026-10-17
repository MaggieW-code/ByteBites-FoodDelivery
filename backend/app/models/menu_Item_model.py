from pydantic import BaseModel, Field

# what the user is allowed to send
class CreateMenuItem(BaseModel):
    name: str = Field(strict = True, min_length = 1)
    category: str = Field(strict = True, min_length = 1)
    price: float = Field(strict = True, gt = 0)
    is_available: bool = Field(strict = True)
    description: str = Field(default="", strict=True)
    


# what the app saves and returns
class MenuItem(CreateMenuItem):
    id: str = Field(strict = True, min_length = 8, max_length = 8)
    restaurant_id: str = Field(strict = True, min_length=8, max_length = 8)


