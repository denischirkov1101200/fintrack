from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.schemas.budget import BudgetCreate, BudgetUpdate


def get_user_budgets(db: Session, user_id: int) -> list[Budget]:
    return db.query(Budget).filter(Budget.user_id == user_id, Budget.is_active == True).all()


def get_budget(db: Session, budget_id: int, user_id: int) -> Budget:
    b = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Бюджет не найден")
    return b


def create_budget(db: Session, user_id: int, data: BudgetCreate) -> Budget:
    budget = Budget(user_id=user_id, **data.model_dump())
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def update_budget(db: Session, budget_id: int, user_id: int, data: BudgetUpdate) -> Budget:
    budget = get_budget(db, budget_id, user_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(budget, key, value)
    db.commit()
    db.refresh(budget)
    return budget


def delete_budget(db: Session, budget_id: int, user_id: int) -> None:
    budget = get_budget(db, budget_id, user_id)
    budget.is_active = False
    db.commit()


def calculate_budget_progress(db: Session, budget: Budget) -> dict:
    start = budget.start_date
    end = budget.end_date or date.today()

    spent = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0.0))
        .filter(
            Transaction.user_id == budget.user_id,
            Transaction.category_id == budget.category_id,
            Transaction.type == "expense",
            Transaction.date >= start,
            Transaction.date <= end,
        )
        .scalar()
    )

    remaining = max(budget.amount - spent, 0)
    progress = min((spent / budget.amount) * 100, 100) if budget.amount > 0 else 0

    return {
        "spent": float(spent),
        "remaining": float(remaining),
        "progress": round(progress, 1),
    }