from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.transaction import Transaction
from app.models.account import Account
from app.schemas.transaction import TransactionCreate, TransactionUpdate


def get_user_transactions(
    db: Session,
    user_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    type_filter: str | None = None,
    category_id: int | None = None,
    account_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Transaction]:
    q = db.query(Transaction).filter(Transaction.user_id == user_id)
    if start_date:
        q = q.filter(Transaction.date >= start_date)
    if end_date:
        q = q.filter(Transaction.date <= end_date)
    if type_filter:
        q = q.filter(Transaction.type == type_filter)
    if category_id:
        q = q.filter(Transaction.category_id == category_id)
    if account_id:
        q = q.filter(Transaction.account_id == account_id)
    return q.order_by(Transaction.date.desc(), Transaction.id.desc()).offset(offset).limit(limit).all()


def get_transaction(db: Session, tx_id: int, user_id: int) -> Transaction:
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == user_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Транзакция не найдена")
    return tx


def create_transaction(db: Session, user_id: int, data: TransactionCreate) -> Transaction:
    account = db.query(Account).filter(Account.id == data.account_id, Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Счёт не найден")

    tx_date = data.date or date.today()
    tx = Transaction(
        user_id=user_id,
        account_id=data.account_id,
        category_id=data.category_id,
        amount=data.amount,
        type=data.type,
        description=data.description,
        date=tx_date,
    )
    db.add(tx)

    if data.type == "income":
        account.balance += data.amount
    else:
        account.balance -= data.amount

    db.commit()
    db.refresh(tx)
    return tx


def update_transaction(db: Session, tx_id: int, user_id: int, data: TransactionUpdate) -> Transaction:
    tx = get_transaction(db, tx_id, user_id)
    account = db.query(Account).filter(Account.id == tx.account_id).first()

    if tx.type == "income":
        account.balance -= tx.amount
    else:
        account.balance += tx.amount

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(tx, key, value)

    if tx.type == "income":
        account.balance += tx.amount
    else:
        account.balance -= tx.amount

    db.commit()
    db.refresh(tx)
    return tx


def delete_transaction(db: Session, tx_id: int, user_id: int) -> None:
    tx = get_transaction(db, tx_id, user_id)
    account = db.query(Account).filter(Account.id == tx.account_id).first()

    if tx.type == "income":
        account.balance -= tx.amount
    else:
        account.balance += tx.amount

    db.delete(tx)
    db.commit()