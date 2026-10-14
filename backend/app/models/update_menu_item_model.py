from pydantic import BaseModel, Field

class UpdateMenuItem(BaseModel):
    name: str | None = Field(default = None, strict = True, min_length = 1)
    category: str | None = Field(default = None, strict = True, min_length = 1)
    price: float | None = Field(default = None, strict = True, gt = 0)
    is_available: bool | None = Field(default = None, strict = True)
    

