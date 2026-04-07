# app/api/anomalies.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from app.db.database import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionResponse, TransactionAnomalyInfo
from app.services.anomaly_detection import AnomalyDetector
from app.core.security import get_current_user

router = APIRouter()


@router.get("/transactions/anomalies")
def get_anomalous_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    level: Optional[str] = Query(None, regex="^(warning|anomaly|alert)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all transactions with anomaly detection applied."""
    
    detector = AnomalyDetector()
    
    # Build base query - filter by user and non-deleted
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.is_deleted == False,
        Transaction.type == "expense"
    )
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    results = []
    stats = {"warning": 0, "anomaly": 0, "alert": 0, "normal": 0, "total_amount": Decimal("0")}
    
    for t in transactions:
        # Calculate category average
        category_avg = detector.calculate_category_average(
            db, t.category_id, t.date, t.type
        )
        
        # Detect anomaly
        anomaly = detector.detect(t.amount, category_avg or Decimal("0"), t.amount)
        
        # Filter by level if requested
        if level and anomaly["level"] != level:
            continue
        
        # Add to results
        if anomaly["level"]:
            stats[anomaly["level"]] += 1
            stats["total_amount"] += t.amount
        else:
            stats["normal"] += 1
        
        results.append({
            **{
                "id": t.id,
                "amount": t.amount,
                "type": t.type,
                "category_id": t.category_id,
                "date": t.date,
                "note": t.note,
                "created_at": t.created_at,
                "tag_ids": []
            },
            "anomaly_info": TransactionAnomalyInfo(
                anomaly_level=anomaly["level"],
                category_monthly_average=category_avg,
                anomaly_reason=anomaly["reason"]
            )
        })
    
    return {
        "items": results,
        "total": len(results),
        "statistics": stats
    }


@router.get("/anomalies/statistics")
def get_anomaly_statistics(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2020),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get anomaly statistics."""
    
    detector = AnomalyDetector()
    
    query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.is_deleted == False,
        Transaction.type == "expense"
    )
    
    if month and year:
        from datetime import date
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        query = query.filter(Transaction.date >= start_date, Transaction.date < end_date)
    
    transactions = query.all()
    
    stats = {"warning": 0, "anomaly": 0, "alert": 0, "normal": 0}
    
    for t in transactions:
        category_avg = detector.calculate_category_average(db, t.category_id, t.date, t.type)
        anomaly = detector.detect(t.amount, category_avg or Decimal("0"), t.amount)
        
        if anomaly["level"]:
            stats[anomaly["level"]] += 1
        else:
            stats["normal"] += 1
    
    return stats
