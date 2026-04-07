"""
OCR API - Upload receipt screenshots and extract transaction data
Supports multiple providers: Tesseract (local), Regex-based parsing
"""

import re
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()

# Allowed image extensions
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}


def parse_amount(text: str) -> float | None:
    """Extract amount from text"""
    patterns = [
        r'[¥￥]?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(?:金额|总额|实付|支付)[:：]?\s*[¥￥]?\s*(\d+(?:\.\d{2})?)',
        r'(\d+(?:\.\d{2})?)\s*(?:元|块)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except:
                pass
    return None


def parse_date(text: str) -> str | None:
    """Extract date from text"""
    patterns = [
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',
        r'(\d{1,2})[/-](\d{1,2})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            groups = match.groups()
            if len(groups) == 3:
                if len(groups[0]) == 4:
                    return f"{groups[0]}-{int(groups[1]):02d}-{int(groups[2]):02d}"
            elif len(groups) == 2:
                import datetime
                now = datetime.datetime.now()
                return f"{now.year}-{int(groups[0]):02d}-{int(groups[1]):02d}"
    return None


def parse_merchant(text: str) -> str | None:
    """Extract merchant from text"""
    patterns = [
        r'(?:商户|商家|收款方|对方)[:：]([^\s]{2,20})',
        r'[\u4e00-\u9fa5]{2,10}(?:店|馆|铺|行|司|中心)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def categorize_by_merchant(merchant: str | None) -> str:
    """Auto-categorize based on merchant name"""
    if not merchant:
        return "其他"
    
    categories = {
        "餐饮": ["快餐", "餐厅", "小吃", "外卖", "麦当劳", "肯德基", "星巴克", "奶茶", "火锅", "烧烤"],
        "交通": ["滴滴", "出租车", "地铁", "公交", "加油", "停车", "打车"],
        "购物": ["淘宝", "京东", "拼多多", "天猫", "超市", "商场", "百货"],
        "娱乐": ["电影", "KTV", "网吧", "游戏", "演出", "健身", "游泳"],
        "医疗": ["医院", "药店", "诊所", "牙科", "体检"],
        "住房": ["房租", "物业", "水电", "燃气"],
        "教育": ["培训", "学费", "书", "教育"],
        "工资": ["工资", "奖金", "兼职", "转账", "收入"],
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in merchant:
                return category
    return "其他"


@router.post("/parse-image")
async def parse_receipt_image(
    file: UploadFile = File(...),
    provider: str = "auto",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Parse receipt/screenshot image and extract transaction data
    
    Args:
        file: Image file (jpg, png, etc.)
        provider: OCR provider - "auto", "tesseract", "regex"
    
    Returns:
        Extracted transaction data (amount, date, merchant, category)
    """
    # Validate file type
    ext = file.filename.split('.')[-1].lower() if file.filename else ''
    if f'.{ext}' not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图片格式: {ext}. 支持的格式: jpg, png, gif, bmp, webp"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size (max 10MB)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片大小超过限制: 10MB"
        )
    
    # Process image with OCR service
    ocr_service: OCRService = get_ocr_service(db)
    
    try:
        result = ocr_service.process_image(content, provider)
    except ImportError as e:
        return {
            "success": False,
            "message": f"OCR服务不可用: {str(e)}",
            "amount": None,
            "date": None,
            "merchant": None,
            "category": "其他"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"OCR处理失败: {str(e)}",
            "amount": None,
            "date": None,
            "merchant": None,
            "category": "其他"
        }
    
    # Check if we got meaningful results
    if result.amount is None and not result.raw_text:
        return {
            "success": False,
            "message": "无法从图片中提取交易信息，请尝试手动输入或使用文本粘贴功能",
            "amount": None,
            "date": None,
            "merchant": None,
            "category": "其他"
        }
    
    return {
        "success": True,
        "amount": str(result.amount) if result.amount else None,
        "date": result.date,
        "merchant": result.merchant,
        "category": result.category or "其他",
        "confidence": result.confidence,
        "type": result.type,
        "note": result.note,
        "raw_text": result.raw_text[:500] if result.raw_text else "",
        "provider": result.provider
    }


@router.post("/parse-text")
def parse_receipt_text(
    text: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Parse receipt text (no OCR needed)"""
    raw_text = text.get("text", "")
    
    amount = parse_amount(raw_text)
    date = parse_date(raw_text)
    merchant = parse_merchant(raw_text)
    category = categorize_by_merchant(merchant)
    
    confidence = 0
    if amount:
        confidence += 30
    if date:
        confidence += 30
    if merchant:
        confidence += 40
    
    return {
        "success": True,
        "amount": amount,
        "date": date,
        "merchant": merchant,
        "category": category,
        "confidence": confidence / 100,
        "note": merchant or "Unknown"
    }


@router.get("/providers")
def get_providers():
    """
    Get available OCR providers
    
    Returns:
        List of available providers with their capabilities
    """
    # Check if tesseract is available
    tesseract_available = False
    try:
        import pytesseract
        tesseract_available = True
    except ImportError:
        pass
    
    return {
        "providers": [
            {
                "id": "auto",
                "name": "自动选择",
                "description": "自动选择最佳可用provider",
                "free": True,
            },
            {
                "id": "tesseract",
                "name": "Tesseract OCR",
                "description": "本地免费OCR引擎，需要安装Tesseract",
                "free": True,
            },
            {
                "id": "regex",
                "name": "正则解析",
                "description": "基于正则表达式的简单解析，作为备选方案",
                "free": True,
            },
        ],
        "tesseract_available": tesseract_available
    }


@router.get("/health")
def health_check():
    """
    Check OCR service health
    
    Returns:
        Service status and available providers
    """
    # Check if tesseract is available
    tesseract_available = False
    try:
        import pytesseract
        tesseract_available = True
    except ImportError:
        pass
    
    return {
        "status": "healthy",
        "providers": {
            "tesseract": tesseract_available,
            "regex": True,
        }
    }
