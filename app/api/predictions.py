from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.prediction import PredictionService
from app.schemas.prediction import PredictionResponse, CurrentMonthActual, PredictionWithActual

router = APIRouter()


@router.get("/predict", response_model=PredictionResponse)
def predict_next_month(db: Session = Depends(get_db)):
    """
    Predict next month's spending using simple moving average.
    
    Algorithm:
    - Based on last 3 months data
    - next_month = avg(last 3 months)
    - confidence range = ±standard deviation (min 15%)
    - Category prediction: same ratio as historical
    """
    service = PredictionService(db)
    prediction = service.predict_next_month()
    return prediction


@router.get("/current-month", response_model=CurrentMonthActual)
def get_current_month_actual(db: Session = Depends(get_db)):
    """Get current month's actual spending"""
    service = PredictionService(db)
    current = service.get_current_month_actual()
    return current


@router.get("/comparison", response_model=PredictionWithActual)
def get_prediction_comparison(db: Session = Depends(get_db)):
    """
    Get prediction with current month actual for comparison.
    Useful for showing predicted vs actual spending.
    """
    service = PredictionService(db)
    prediction = service.predict_next_month()
    current_month = service.get_current_month_actual()
    
    # Calculate projected vs actual percentage
    if prediction['predicted_total'] > 0:
        projected_vs_actual = ((current_month['actual_total'] / prediction['predicted_total']) - 1) * 100
    else:
        projected_vs_actual = 0
    
    return {
        'prediction': prediction,
        'current_month': current_month,
        'projected_vs_actual': round(projected_vs_actual, 1)
    }
