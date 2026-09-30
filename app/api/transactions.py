from datetime import date
from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import csv
import io
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionOut
from app.services import transaction as tx_service

router = APIRouter(prefix="/transactions", tags=["Транзакции"])


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    start_date: date | None = None,
    end_date: date | None = None,
    type: str | None = Query(None, pattern="^(income|expense)$"),
    category_id: int | None = None,
    account_id: int | None = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    txs = tx_service.get_user_transactions(
        db, current_user.id, start_date, end_date, type, category_id, account_id, limit, offset
    )
    result = []
    for tx in txs:
        out = TransactionOut.model_validate(tx)
        out.category_name = tx.category.name if tx.category else None
        out.account_name = tx.account.name if tx.account else None
        result.append(out)
    return result


@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx = tx_service.create_transaction(db, current_user.id, data)
    out = TransactionOut.model_validate(tx)
    out.category_name = tx.category.name if tx.category else None
    out.account_name = tx.account.name if tx.account else None
    return out


@router.get("/export")
def export_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    txs = tx_service.get_user_transactions(db, current_user.id, limit=10000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Дата", "Тип", "Сумма", "Категория", "Счёт", "Описание"])
    for tx in txs:
        writer.writerow([
            tx.id,
            tx.date.isoformat(),
            "Доход" if tx.type == "income" else "Расход",
            tx.amount,
            tx.category.name if tx.category else "",
            tx.account.name if tx.account else "",
            tx.description or "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )


@router.get("/{tx_id}", response_model=TransactionOut)
def get_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx = tx_service.get_transaction(db, tx_id, current_user.id)
    out = TransactionOut.model_validate(tx)
    out.category_name = tx.category.name if tx.category else None
    out.account_name = tx.account.name if tx.account else None
    return out


@router.patch("/{tx_id}", response_model=TransactionOut)
def update_transaction(
    tx_id: int,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx = tx_service.update_transaction(db, tx_id, current_user.id, data)
    out = TransactionOut.model_validate(tx)
    out.category_name = tx.category.name if tx.category else None
    out.account_name = tx.account.name if tx.account else None
    return out


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tx_service.delete_transaction(db, tx_id, current_user.id)