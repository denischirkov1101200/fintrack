from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern="^(income|expense)$")
    icon: str = "tag"
    color: str = "#8b5cf6"


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None
    color: str | None = None
    is_active: bool | None = None


class CategoryOut(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)