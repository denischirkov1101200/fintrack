from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetOut
from app.services import budget as budget_service

router = APIRouter(prefix="/budgets", tags=["Бюджеты"])


@router.get("", response_model=list[BudgetOut])
def list_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budgets = budget_service.get_user_budgets(db, current_user.id)
    result = []
    for b in budgets:
        progress = budget_service.calculate_budget_progress(db, b)
        out = BudgetOut.model_validate(b)
        out.category_name = b.category.name if b.category else None
        out.spent = progress["spent"]
        out.remaining = progress["remaining"]
        out.progress = progress["progress"]
        result.append(out)
    return result


@router.post("", response_model=BudgetOut, status_code=status.HTTP_201_CREATED)
def create_budget(
    data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    b = budget_service.create_budget(db, current_user.id, data)
    progress = budget_service.calculate_budget_progress(db, b)
    out = BudgetOut.model_validate(b)
    out.category_name = b.category.name if b.category else None
    out.spent = progress["spent"]
    out.remaining = progress["remaining"]
    out.progress = progress["progress"]
    return out


@router.patch("/{budget_id}", response_model=BudgetOut)
def update_budget(
    budget_id: int,
    data: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    b = budget_service.update_budget(db, budget_id, current_user.id, data)
    progress = budget_service.calculate_budget_progress(db, b)
    out = BudgetOut.model_validate(b)
    out.category_name = b.category.name if b.category else None
    out.spent = progress["spent"]
    out.remaining = progress["remaining"]
    out.progress = progress["progress"]
    return out


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget_service.delete_budget(db, budget_id, current_user.id)