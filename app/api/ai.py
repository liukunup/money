"""
AI API - Provider management and transaction classification
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.db.database import get_db
from app.models.ai_provider import AIProvider
from app.models.category import Category
from app.schemas.ai_provider import (
    AIProviderCreate, AIProviderUpdate, AIProviderResponse, 
    SUPPORTED_PROVIDERS
)
from app.services.ai_service import AIService, get_ai_service

router = APIRouter()


# ==================== AI Provider Management ====================

@router.get("/providers", response_model=List[AIProviderResponse])
def get_providers(
    include_inactive: bool = False,
    db: Session = Depends(get_db)
):
    """Get all AI providers"""
    query = db.query(AIProvider)
    if not include_inactive:
        query = query.filter(AIProvider.is_active == True)
    providers = query.order_by(AIProvider.priority.asc()).all()
    return providers


@router.get("/providers/supported")
def get_supported_providers():
    """Get list of supported AI providers"""
    return SUPPORTED_PROVIDERS


@router.post("/providers", response_model=AIProviderResponse, status_code=status.HTTP_201_CREATED)
def create_provider(
    provider: AIProviderCreate,
    db: Session = Depends(get_db)
):
    """Create a new AI provider"""
    data = provider.model_dump()
    if data.get('models'):
        data['models'] = json.dumps(data['models'])
    db_provider = AIProvider(**data)
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider


@router.get("/providers/{provider_id}", response_model=AIProviderResponse)
def get_provider(provider_id: int, db: Session = Depends(get_db)):
    """Get a single AI provider"""
    provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Provider not found"
        )
    return provider


@router.put("/providers/{provider_id}", response_model=AIProviderResponse)
def update_provider(
    provider_id: int,
    provider_update: AIProviderUpdate,
    db: Session = Depends(get_db)
):
    """Update an AI provider"""
    provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Provider not found"
        )
    
    update_data = provider_update.model_dump(exclude_unset=True)
    
    # Convert models list to JSON string if present
    if 'models' in update_data and update_data['models'] is not None:
        update_data['models'] = json.dumps(update_data['models'])
    
    for field, value in update_data.items():
        setattr(provider, field, value)
    
    db.commit()
    db.refresh(provider)
    return provider


@router.delete("/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider(provider_id: int, db: Session = Depends(get_db)):
    """Delete an AI provider"""
    provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Provider not found"
        )
    
    db.delete(provider)
    db.commit()
    return None


@router.post("/providers/{provider_id}/toggle", response_model=AIProviderResponse)
def toggle_provider(provider_id: int, db: Session = Depends(get_db)):
    """Toggle AI provider active status"""
    provider = db.query(AIProvider).filter(AIProvider.id == provider_id).first()
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI Provider not found"
        )
    
    provider.is_active = not provider.is_active
    db.commit()
    db.refresh(provider)
    return provider


# ==================== Transaction Classification ====================

@router.post("/classify")
async def classify_transaction(
    amount: float = Query(..., description="Transaction amount"),
    transaction_type: str = Query(..., description="Transaction type: income or expense"),
    note: str = Query("", description="Transaction note/description"),
    db: Session = Depends(get_db)
):
    """Classify a transaction using AI"""
    
    # Get all active categories
    categories = db.query(Category).filter(
        Category.is_deleted == False
    ).all()
    
    if not categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No categories available"
        )
    
    category_list = [
        {"id": c.id, "name": c.name, "type": c.type} 
        for c in categories
    ]
    
    # Get AI service and classify
    ai_service = get_ai_service(db)
    result = await ai_service.classify_transaction(
        amount=amount,
        transaction_type=transaction_type,
        note=note,
        categories=category_list
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Classification failed. Please check AI provider configuration."
        )
    
    # Get category info
    category = next(
        (c for c in categories if c.id == result.get('category_id')), 
        None
    )
    
    return {
        "category_id": result.get('category_id'),
        "confidence": result.get('confidence', 0),
        "reason": result.get('reason', ''),
        "category_name": category.name if category else None,
        "is_keyword_fallback": result.get('is_keyword_fallback', False)
    }


@router.post("/suggestions")
async def get_suggestions(
    note: str = Query(..., description="Transaction note/description"),
    limit: int = Query(3, ge=1, le=10, description="Maximum number of suggestions"),
    db: Session = Depends(get_db)
):
    """Get category suggestions for a transaction note"""
    
    # Get all active categories
    categories = db.query(Category).filter(
        Category.is_deleted == False
    ).all()
    
    if not categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No categories available"
        )
    
    category_list = [
        {"id": c.id, "name": c.name, "type": c.type} 
        for c in categories
    ]
    
    # Get AI service and get suggestions
    ai_service = get_ai_service(db)
    suggestions = await ai_service.get_suggestions(
        note=note,
        categories=category_list,
        limit=limit
    )
    
    # Enrich with category info
    enriched_suggestions = []
    for suggestion in suggestions:
        category = next(
            (c for c in categories if c.id == suggestion.get('category_id')), 
            None
        )
        if category:
            enriched_suggestions.append({
                "category_id": category.id,
                "category_name": category.name,
                "category_icon": category.icon,
                "reason": suggestion.get('reason', '')
            })
    
    return {
        "suggestions": enriched_suggestions,
        "note": note
    }


# ==================== Settings ====================

@router.get("/settings")
def get_ai_settings(db: Session = Depends(get_db)):
    """Get AI feature settings"""
    active_providers = db.query(AIProvider).filter(
        AIProvider.is_active == True
    ).count()
    
    return {
        "ai_enabled": active_providers > 0,
        "active_provider_count": active_providers,
        "total_provider_count": db.query(AIProvider).count()
    }
