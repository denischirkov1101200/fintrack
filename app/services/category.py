from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_user_categories(db: Session, user_id: int, type_filter: str | None = None) -> list[Category]:
    q = db.query(Category).filter(Category.user_id == user_id, Category.is_active == True)
    if type_filter:
        q = q.filter(Category.type == type_filter)
    return q.all()


def get_category(db: Session, category_id: int, user_id: int) -> Category:
    cat = db.query(Category).filter(Category.id == category_id, Category.user_id == user_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return cat


def create_category(db: Session, user_id: int, data: CategoryCreate) -> Category:
    cat = Category(user_id=user_id, **data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def update_category(db: Session, category_id: int, user_id: int, data: CategoryUpdate) -> Category:
    cat = get_category(db, category_id, user_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, key, value)
    db.commit()
    db.refresh(cat)
    return cat


def delete_category(db: Session, category_id: int, user_id: int) -> None:
    cat = get_category(db, category_id, user_id)
    cat.is_active = False
    db.commit()