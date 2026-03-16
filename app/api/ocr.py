import re
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Parse receipt/screenshot image using regex-based OCR fallback"""
    # For now, return a placeholder response
    # In production, you would integrate with an OCR service
    return {
        "success": False,
        "message": "OCR service not configured. Please use text paste instead.",
        "amount": None,
        "date": None,
        "merchant": None,
        "category": "其他"
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
