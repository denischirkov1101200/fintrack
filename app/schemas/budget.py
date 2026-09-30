from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict


class BudgetBase(BaseModel):
    category_id: int
    amount: float = Field(..., gt=0)
    period: str = Field(default="monthly", pattern="^(monthly|weekly)$")
    start_date: date
    end_date: date | None = None


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    amount: float | None = Field(None, gt=0)
    period: str | None = Field(None, pattern="^(monthly|weekly)$")
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class BudgetOut(BudgetBase):
    id: int
    is_active: bool
    created_at: datetime
    category_name: str | None = None
    spent: float = 0.0
    remaining: float = 0.0
    progress: float = 0.0
    model_config = ConfigDict(from_attributes=True)