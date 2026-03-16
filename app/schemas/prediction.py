from pydantic import BaseModel
from typing import List, Optional


class MonthlyHistory(BaseModel):
    year: int
    month: int
    total: float


class CategoryPrediction(BaseModel):
    category_id: int
    category_name: str
    category_icon: Optional[str] = None
    predicted_amount: float
    ratio: float
    confidence_low: float
    confidence_high: float


class PredictionResponse(BaseModel):
    predicted_total: float
    confidence_low: float
    confidence_high: float
    based_on_months: int
    monthly_history: List[MonthlyHistory]
    category_predictions: List[CategoryPrediction]


class CurrentMonthActual(BaseModel):
    actual_total: float
    month: int
    year: int
    day_of_month: int
    days_in_month: int


class PredictionWithActual(BaseModel):
    prediction: PredictionResponse
    current_month: CurrentMonthActual
    projected_vs_actual: float  # percentage difference
