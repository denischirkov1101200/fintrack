from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate


def get_user_accounts(db: Session, user_id: int) -> list[Account]:
    return db.query(Account).filter(Account.user_id == user_id, Account.is_active == True).all()


def get_account(db: Session, account_id: int, user_id: int) -> Account:
    account = db.query(Account).filter(Account.id == account_id, Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Счёт не найден")
    return account


def create_account(db: Session, user_id: int, data: AccountCreate) -> Account:
    account = Account(user_id=user_id, **data.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def update_account(db: Session, account_id: int, user_id: int, data: AccountUpdate) -> Account:
    account = get_account(db, account_id, user_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(account, key, value)
    db.commit()
    db.refresh(account)
    return account


def delete_account(db: Session, account_id: int, user_id: int) -> None:
    account = get_account(db, account_id, user_id)
    account.is_active = False
    db.commit()