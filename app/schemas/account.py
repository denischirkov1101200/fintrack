from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    currency: str = "RUB"
    icon: str = "wallet"
    color: str = "#6366f1"


class AccountCreate(AccountBase):
    balance: float = 0.0


class AccountUpdate(BaseModel):
    name: str | None = None
    currency: str | None = None
    icon: str | None = None
    color: str | None = None
    is_active: bool | None = None


class AccountOut(AccountBase):
    id: int
    balance: float
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)