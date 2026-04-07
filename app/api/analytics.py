from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.user import User
from app.core.security import get_current_user
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/anomalies")
def get_anomalies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get anomalous transactions based on statistical analysis"""
    # Get all transactions for the user
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.is_deleted == False
    ).all()
    
    if not transactions:
        return {"transactions": [], "summary": {"total": 0, "warnings": 0, "anomalies": 0}}
    
    # Calculate category averages
    category_totals = {}
    category_counts = {}
    
    for t in transactions:
        if t.category_id not in category_totals:
            category_totals[t.category_id] = 0
            category_counts[t.category_id] = 0
        category_totals[t.category_id] += abs(t.amount)
        category_counts[t.category_id] += 1
    
    # Calculate averages
    category_averages = {}
    for cat_id in category_totals:
        if category_counts[cat_id] > 0:
            category_averages[cat_id] = category_totals[cat_id] / category_counts[cat_id]
    
    # Get category names
    categories = db.query(Category).filter(Category.id.in_(category_averages.keys())).all()
    category_names = {c.id: c.name for c in categories}
    
    # Find anomalies
    warnings = []
    anomalies = []
    
    for t in transactions:
        if not t.category_id or t.type == "income":
            continue
        
        avg = category_averages.get(t.category_id, 0)
        if avg == 0:
            continue
            
        ratio = abs(t.amount) / avg
        
        # Get category name
        category_name = category_names.get(t.category_id, "Unknown")
        
        t_data = {
            "id": t.id,
            "amount": t.amount,
            "date": t.date,
            "note": t.note,
            "category": category_name,
            "ratio": round(ratio, 1)
        }
        
        if ratio > 3:
            anomalies.append({**t_data, "level": "anomaly", "message": f"超过平均 {ratio:.1f} 倍"})
        elif ratio > 2:
            warnings.append({**t_data, "level": "warning", "message": f"超过平均 {ratio:.1f} 倍"})
    
    return {
        "transactions": warnings + anomalies,
        "summary": {
            "total": len(transactions),
            "warnings": len(warnings),
            "anomalies": len(anomalies)
        }
    }


@router.get("/prediction")
def get_spending_prediction(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Predict next month spending based on historical data"""
    # Get last 3 months of data
    today = datetime.now()
    three_months_ago = today - timedelta(days=90)
    
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.is_deleted == False,
        Transaction.date >= three_months_ago.date(),
        Transaction.type == "expense"
    ).all()
    
    if not transactions:
        return {
            "predicted_total": 0,
            "confidence": "low",
            "message": "暂无足够数据"
        }
    
    # Calculate monthly totals
    monthly_totals = {}
    for t in transactions:
        month_key = f"{t.date.year}-{t.date.month:02d}"
        if month_key not in monthly_totals:
            monthly_totals[month_key] = 0
        monthly_totals[month_key] += abs(t.amount)
    
    # Calculate prediction (simple moving average)
    if len(monthly_totals) >= 2:
        avg = sum(monthly_totals.values()) / len(monthly_totals)
        predicted = avg
        confidence = "medium" if len(monthly_totals) >= 3 else "low"
    else:
        # Not enough data, use single month
        predicted = list(monthly_totals.values())[0] if monthly_totals else 0
        confidence = "low"
    
    # Category breakdown prediction
    category_totals = {}
    for t in transactions:
        if t.category_id:
            cat = db.query(Category).filter(Category.id == t.category_id).first()
            if cat:
                if cat.name not in category_totals:
                    category_totals[cat.name] = 0
                category_totals[cat.name] += abs(t.amount)
    
    # Calculate percentages
    total = sum(category_totals.values())
    category_breakdown = []
    for name, amount in category_totals.items():
        category_breakdown.append({
            "category": name,
            "predicted": round(amount / len(monthly_totals) if monthly_totals else amount, 2),
            "percentage": round(amount / total * 100, 1) if total > 0 else 0
        })
    
    return {
        "predicted_total": round(predicted, 2),
        "confidence": confidence,
        "confidence_display": "中" if confidence == "medium" else "低",
        "based_on_months": len(monthly_totals),
        "monthly_averages": monthly_totals,
        "category_breakdown": sorted(category_breakdown, key=lambda x: x["predicted"], reverse=True),
        "message": f"基于过去 {len(monthly_totals)} 个月的数据预测"
    }
