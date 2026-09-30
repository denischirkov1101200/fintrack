from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token


def register_user(db: Session, user_in: UserCreate) -> User:
    existing = db.query(User).filter(
        (User.email == user_in.email) | (User.username == user_in.username)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email или username уже существует",
        )
    user = User(
        email=user_in.email,
        username=user_in.username,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_tokens(user: User) -> dict:
    access = create_access_token(subject=user.id)
    refresh = create_refresh_token(subject=user.id)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
    }