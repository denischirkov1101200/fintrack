from pydantic import BaseModel
from typing import List


class CategoryExpense(BaseModel):
    category_id: int
    category_name: str
    color: str
    total: float
    percentage: float


class MonthlyStat(BaseModel):
    month: str
    income: float
    expense: float


class BalancePoint(BaseModel):
    date: str
    balance: float


class DashboardStats(BaseModel):
    total_balance: float
    total_income: float
    total_expense: float
    period_income: float
    period_expense: float
    expense_by_category: List[CategoryExpense]
    monthly_stats: List[MonthlyStat]
    balance_history: List[BalancePoint]
    top_expense_categories: List[CategoryExpense]