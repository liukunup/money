# app/services/anomaly_detection.py
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.transaction import Transaction


class AnomalyDetector:
    """Service for detecting anomalous transactions."""
    
    def __init__(
        self,
        warning_threshold: float = 2.0,
        anomaly_threshold: float = 3.0,
        large_transaction_threshold: float = 10000.0
    ):
        self.warning_threshold = warning_threshold
        self.anomaly_threshold = anomaly_threshold
        self.large_transaction_threshold = large_transaction_threshold
    
    def detect(
        self,
        amount: Decimal,
        category_average: Decimal,
        absolute_amount: Decimal
    ) -> Dict[str, Any]:
        """
        Detect anomaly level for a transaction.
        
        Returns dict with:
        - level: "warning" | "anomaly" | "alert" | None
        - reason: explanation string
        """
        # Check absolute threshold first (alert)
        if absolute_amount >= Decimal(str(self.large_transaction_threshold)):
            return {
                "level": "alert",
                "reason": f"Large transaction: {absolute_amount} >= {self.large_transaction_threshold}"
            }
        
        # Check category-based thresholds (only for expenses)
        if category_average and category_average > 0:
            ratio = amount / category_average
            
            if ratio >= Decimal(str(self.anomaly_threshold)):
                return {
                    "level": "anomaly",
                    "reason": f"Amount {amount} is {ratio:.1f}x category average ({category_average})"
                }
            elif ratio >= Decimal(str(self.warning_threshold)):
                return {
                    "level": "warning",
                    "reason": f"Amount {amount} is {ratio:.1f}x category average ({category_average})"
                }
        
        return {"level": None, "reason": None}
    
    def calculate_category_average(
        self,
        db: Session,
        category_id: int,
        transaction_date: date,
        transaction_type: str = "expense"
    ) -> Optional[Decimal]:
        """
        Calculate monthly average for a category based on historical data.
        Uses all months except the current month.
        """
        # Get year and month of the transaction
        year = transaction_date.year
        month = transaction_date.month
        
        # Query for all transactions in this category, same type, 
        # excluding the current month
        query = db.query(func.avg(Transaction.amount)).filter(
            Transaction.category_id == category_id,
            Transaction.type == transaction_type,
            Transaction.is_deleted == False
        )
        
        # Exclude current month
        query = query.filter(
            ~(
                (func.extract('year', Transaction.date) == year) &
                (func.extract('month', Transaction.date) == month)
            )
        )
        
        result = query.scalar()
        return Decimal(str(result)) if result else None
