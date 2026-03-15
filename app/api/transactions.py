from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List, Optional
from datetime import date, datetime
from app.db.database import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    type: Optional[str] = None,
    category_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    include_deleted: bool = False,
    db: Session = Depends(get_db)
):
    """获取交易列表（支持筛选）"""
    query = db.query(Transaction)

    if not include_deleted:
        query = query.filter(Transaction.is_deleted == False)

    if type:
        query = query.filter(Transaction.type == type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.order_by(Transaction.date.desc()).all()
    return transactions

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """创建交易"""
    db_transaction = Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """获取单个交易"""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == False
    ).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易不存在"
        )
    return transaction

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """更新交易"""
    db_transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == False
    ).first()
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易不存在"
        )

    update_data = transaction.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_transaction, field, value)

    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """软删除交易"""
    db_transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == False
    ).first()
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易不存在"
        )

    db_transaction.is_deleted = True
    db_transaction.deleted_at = datetime.utcnow()
    db_transaction.deleted_by = current_user.id

    db.commit()
    return None

@router.post("/{transaction_id}/restore", response_model=TransactionResponse)
def restore_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """恢复已删除的交易"""
    db_transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == True
    ).first()
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易不存在或未被删除"
        )

    db_transaction.is_deleted = False
    db_transaction.deleted_at = None
    db_transaction.deleted_by = None

    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/recycle-bin/list", response_model=List[TransactionResponse])
def get_deleted_transactions(
    db: Session = Depends(get_db)
):
    """获取回收站中的交易列表"""
    transactions = db.query(Transaction).filter(
        Transaction.is_deleted == True
    ).order_by(Transaction.deleted_at.desc()).all()
    return transactions

@router.delete("/recycle-bin/{transaction_id}/permanently", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):
    """永久删除交易（从回收站移除）"""
    db_transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == True
    ).first()
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="交易不存在或未被删除"
        )

    db.delete(db_transaction)
    db.commit()
    return None

@router.delete("/recycle-bin/permanently", status_code=status.HTTP_204_NO_CONTENT)
def permanently_delete_all(
    days: int = Query(30, description="删除N天前的数据"),
    db: Session = Depends(get_db)
):
    """永久删除N天前软删除的交易"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    db.query(Transaction).filter(
        Transaction.is_deleted == True,
        Transaction.deleted_at < cutoff_date
    ).delete()

    db.commit()
    return None
