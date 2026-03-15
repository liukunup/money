from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from app.services.text_parser import parse_text, to_dict, ParsedTransaction

router = APIRouter()


class TextParseRequest(BaseModel):
    """Request model for text parsing"""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to parse (SMS, receipt, etc.)")


class TextParseResponse(BaseModel):
    """Response model for parsed transaction"""
    amount: Optional[str] = Field(None, description="Extracted amount")
    date: Optional[str] = Field(None, description="Extracted date (YYYY-MM-DD)")
    category: Optional[str] = Field(None, description="Detected category")
    merchant: Optional[str] = Field(None, description="Detected merchant/store name")
    note: Optional[str] = Field(None, description="Generated note from parsed data")
    type: str = Field("expense", description="Transaction type: income or expense")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Parsing confidence score")
    format_type: str = Field("unknown", description="Detected text format: alipay, wechat, sms, plain")


@router.post("/parse", response_model=TextParseResponse)
def parse_text_endpoint(request: TextParseRequest):
    """
    Parse text to extract transaction data.
    
    Supports:
    - Alipay SMS: "【支付宝】您在XX消费35.50元"
    - WeChat Pay: "微信支付凭证\n商户：XX\n金额：42.00元"
    - Plain text: "今天中午在麦当劳花了45元"
    - Any other text format with amount and date information
    """
    try:
        parsed = parse_text(request.text)
        return TextParseResponse(**to_dict(parsed))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse text: {str(e)}"
        )
