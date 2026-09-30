from datetime import date, timedelta
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.analytics import (
    DashboardStats,
    CategoryExpense,
    MonthlyStat,
    BalancePoint,
)


def get_dashboard_stats(
    db: Session,
    user_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
) -> DashboardStats:
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    total_balance = (
        db.query(func.coalesce(func.sum(Account.balance), 0.0))
        .filter(Account.user_id == user_id, Account.is_active == True)
        .scalar()
    )

    total_income = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0.0))
        .filter(Transaction.user_id == user_id, Transaction.type == "income")
        .scalar()
    )
    total_expense = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0.0))
        .filter(Transaction.user_id == user_id, Transaction.type == "expense")
        .scalar()
    )

    period_income = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0.0))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "income",
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        )
        .scalar()
    )
    period_expense = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0.0))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        )
        .scalar()
    )

    cat_rows = (
        db.query(
            Category.id,
            Category.name,
            Category.color,
            func.sum(Transaction.amount).label("total"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        )
        .group_by(Category.id, Category.name, Category.color)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    total_exp = float(period_expense) or 1.0
    expense_by_category = [
        CategoryExpense(
            category_id=r.id,
            category_name=r.name,
            color=r.color,
            total=float(r.total),
            percentage=round((float(r.total) / total_exp) * 100, 1),
        )
        for r in cat_rows
    ]

    monthly_rows = (
        db.query(
            extract("year", Transaction.date).label("year"),
            extract("month", Transaction.date).label("month"),
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        )
        .filter(
            Transaction.user_id == user_id,
            Transaction.date >= end_date - timedelta(days=180),
        )
        .group_by("year", "month", Transaction.type)
        .all()
    )

    monthly_map: dict[str, dict] = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for r in monthly_rows:
        key = f"{int(r.year)}-{int(r.month):02d}"
        monthly_map[key][r.type] = float(r.total)

    monthly_stats = [
        MonthlyStat(month=k, income=v["income"], expense=v["expense"])
        for k, v in sorted(monthly_map.items())
    ]

    txs = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
        )
        .order_by(Transaction.date)
        .all()
    )

    start_balance = float(total_balance)
    for t in reversed(txs):
        if t.type == "income":
            start_balance -= t.amount
        else:
            start_balance += t.amount

    balance = start_balance
    history_map: dict[str, float] = {}
    for t in txs:
        if t.type == "income":
            balance += t.amount
        else:
            balance -= t.amount
        history_map[t.date.isoformat()] = round(balance, 2)

    balance_history = [
        BalancePoint(date=k, balance=v) for k, v in sorted(history_map.items())
    ]

    return DashboardStats(
        total_balance=round(float(total_balance), 2),
        total_income=round(float(total_income), 2),
        total_expense=round(float(total_expense), 2),
        period_income=round(float(period_income), 2),
        period_expense=round(float(period_expense), 2),
        expense_by_category=expense_by_category,
        monthly_stats=monthly_stats,
        balance_history=balance_history,
        top_expense_categories=expense_by_category[:5],
    )