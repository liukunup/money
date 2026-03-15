from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List
from datetime import date, timedelta
from decimal import Decimal
from app.models.transaction import Transaction
from app.models.category import Category


class PredictionService:
    """Spending prediction service using simple moving average"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_monthly_totals(self, months: int = 3) -> List[Dict]:
        """Get total expenses for the last N months"""
        today = date.today()
        results = []
        
        for i in range(months):
            # Calculate month range
            target_month = today.month - i
            target_year = today.year
            
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            
            # First day of month
            start_date = date(target_year, target_month, 1)
            
            # Last day of month
            if target_month == 12:
                end_date = date(target_year, 12, 31)
            else:
                next_month = target_month + 1
                next_year = target_year
                if next_month > 12:
                    next_month = 1
                    next_year += 1
                end_date = date(next_year, next_month, 1) - timedelta(days=1)
            
            # Query total for this month
            total = self.db.query(func.sum(Transaction.amount)).filter(
                Transaction.type == 'expense',
                Transaction.is_deleted == False,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).scalar() or Decimal('0')
            
            results.append({
                'year': target_year,
                'month': target_month,
                'total': float(total),
                'start_date': start_date,
                'end_date': end_date
            })
        
        return results
    
    def get_category_breakdown(self, months: int = 3) -> Dict[int, float]:
        """Get expense breakdown by category for the last N months"""
        today = date.today()
        
        # Calculate start date (3 months ago)
        start_month = today.month - months
        start_year = today.year
        while start_month <= 0:
            start_month += 12
            start_year -= 1
        start_date = date(start_year, start_month, 1)
        
        # Query expenses by category
        results = self.db.query(
            Transaction.category_id,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.type == 'expense',
            Transaction.is_deleted == False,
            Transaction.date >= start_date,
            Transaction.date <= today
        ).group_by(Transaction.category_id).all()
        
        return {row.category_id: float(row.total) for row in results}
    
    def predict_next_month(self) -> Dict:
        """
        Predict next month's spending using simple moving average.
        
        Algorithm:
        - next_month = avg(last 3 months)
        - confidence range = ±20% (simple approach)
        - Category prediction: same ratio as historical
        """
        # Get last 3 months data
        monthly_totals = self.get_monthly_totals(months=3)
        
        if not monthly_totals or all(m['total'] == 0 for m in monthly_totals):
            return {
                'predicted_total': 0,
                'confidence_low': 0,
                'confidence_high': 0,
                'based_on_months': 0,
                'monthly_history': [],
                'category_predictions': []
            }
        
        # Calculate moving average
        totals = [m['total'] for m in monthly_totals if m['total'] > 0]
        
        if not totals:
            return {
                'predicted_total': 0,
                'confidence_low': 0,
                'confidence_high': 0,
                'based_on_months': 0,
                'monthly_history': [],
                'category_predictions': []
            }
        
        predicted_total = sum(totals) / len(totals)
        
        # Calculate standard deviation for confidence range
        if len(totals) > 1:
            mean = predicted_total
            variance = sum((x - mean) ** 2 for x in totals) / len(totals)
            std_dev = variance ** 0.5
            # Use 1 std dev for confidence range, minimum 15%
            confidence_factor = max(std_dev / mean if mean > 0 else 0, 0.15)
        else:
            # Single month - use 20% as default confidence
            confidence_factor = 0.20
        
        confidence_low = predicted_total * (1 - confidence_factor)
        confidence_high = predicted_total * (1 + confidence_factor)
        
        # Get category breakdown for prediction
        category_breakdown = self.get_category_breakdown(months=3)
        total_by_category = sum(category_breakdown.values())
        
        category_predictions = []
        if total_by_category > 0:
            # Get category info
            categories = self.db.query(Category).filter(
                Category.id.in_(category_breakdown.keys()),
                Category.is_deleted == False
            ).all()
            
            category_map = {c.id: c for c in categories}
            
            for cat_id, amount in category_breakdown.items():
                ratio = amount / total_by_category
                predicted_amount = predicted_total * ratio
                category = category_map.get(cat_id)
                
                if category:
                    category_predictions.append({
                        'category_id': cat_id,
                        'category_name': category.name,
                        'category_icon': category.icon,
                        'predicted_amount': round(predicted_amount, 2),
                        'ratio': round(ratio * 100, 1),
                        'confidence_low': round(predicted_amount * (1 - confidence_factor), 2),
                        'confidence_high': round(predicted_amount * (1 + confidence_factor), 2)
                    })
        
        # Sort by predicted amount descending
        category_predictions.sort(key=lambda x: x['predicted_amount'], reverse=True)
        
        return {
            'predicted_total': round(predicted_total, 2),
            'confidence_low': round(confidence_low, 2),
            'confidence_high': round(confidence_high, 2),
            'based_on_months': len([m for m in monthly_totals if m['total'] > 0]),
            'monthly_history': [
                {
                    'year': m['year'],
                    'month': m['month'],
                    'total': round(m['total'], 2)
                }
                for m in monthly_totals
            ],
            'category_predictions': category_predictions[:8]  # Top 8 categories
        }
    
    def get_current_month_actual(self) -> Dict:
        """Get current month's actual spending"""
        today = date.today()
        start_date = date(today.year, today.month, 1)
        
        total = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.type == 'expense',
            Transaction.is_deleted == False,
            Transaction.date >= start_date,
            Transaction.date <= today
        ).scalar() or Decimal('0')
        
        return {
            'actual_total': float(total),
            'month': today.month,
            'year': today.year,
            'day_of_month': today.day,
            'days_in_month': self._days_in_month(today.year, today.month)
        }
    
    def _days_in_month(self, year: int, month: int) -> int:
        """Get number of days in a month"""
        if month == 12:
            return 31
        next_month = date(year + (month // 12), (month % 12) + 1, 1)
        return (next_month - timedelta(days=1)).day
