from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.account import AccountCreate, AccountUpdate, AccountOut
from app.services import account as account_service

router = APIRouter(prefix="/accounts", tags=["Счета"])


@router.get("", response_model=list[AccountOut])
def list_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return account_service.get_user_accounts(db, current_user.id)


@router.post("", response_model=AccountOut, status_code=status.HTTP_201_CREATED)
def create_account(
    data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return account_service.create_account(db, current_user.id, data)


@router.get("/{account_id}", response_model=AccountOut)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return account_service.get_account(db, account_id, current_user.id)


@router.patch("/{account_id}", response_model=AccountOut)
def update_account(
    account_id: int,
    data: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return account_service.update_account(db, account_id, current_user.id, data)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account_service.delete_account(db, account_id, current_user.id)