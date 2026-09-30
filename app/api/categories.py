from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.services import category as category_service

router = APIRouter(prefix="/categories", tags=["Категории"])


@router.get("", response_model=list[CategoryOut])
def list_categories(
    type: str | None = Query(None, pattern="^(income|expense)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.get_user_categories(db, current_user.id, type)


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.create_category(db, current_user.id, data)


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.get_category(db, category_id, current_user.id)


@router.patch("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return category_service.update_category(db, category_id, current_user.id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category_service.delete_category(db, category_id, current_user.id)