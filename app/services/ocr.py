"""
OCR Service - Extract transaction data from receipt screenshots
Supports multiple providers: Tesseract (local), Regex-based parsing
"""

import re
import io
from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal
from dataclasses import dataclass

from app.models.category import Category

# Category keywords for auto-classification
CATEGORY_KEYWORDS = {
    "餐饮": ["午餐", "晚餐", "早餐", "外卖", "餐厅", "麦当劳", "肯德基", "星巴克", "瑞幸", "奶茶", "小吃", "烧烤", "火锅", "冒菜", "黄焖鸡", "沙县", "兰州拉面", "便利店", "全家", "罗森", "7-11"],
    "交通": ["地铁", "公交", "出租车", "滴滴", "加油", "停车", "高速", "打车", "网约车", "共享单车", "火车", "高铁", "飞机", "长途"],
    "购物": ["淘宝", "京东", "拼多多", "天猫", "超市", "苏宁", "国美", "唯品会", "蘑菇街", "网易严选", "小米", "苹果", "华为"],
    "娱乐": ["电影", "游戏", "KTV", "音乐", "视频", "爱奇艺", "优酷", "腾讯视频", "B站", "网易云", "QQ音乐", "健身", "游泳", "羽毛球", "篮球", "足球"],
    "住房": ["房租", "水电", "燃气", "物业", "宽带", "话费", "中介", "维修", "保洁"],
    "医疗": ["药店", "医院", "门诊", "体检", "保险", "医保", "牙科", "眼科"],
    "教育": ["学费", "培训", "课程", "书籍", "文具", "教育", "辅导", "留学"],
}


@dataclass
class OCRResult:
    """Result from OCR processing"""
    amount: Optional[Decimal] = None
    date: Optional[str] = None
    merchant: Optional[str] = None
    category: Optional[str] = None
    note: Optional[str] = None
    type: str = "expense"
    confidence: float = 0.0
    raw_text: str = ""
    provider: str = "regex"


class OCRService:
    """OCR Service with multiple provider support"""
    
    def __init__(self, db_session=None):
        self.db = db_session
        self.categories_map: Dict[str, int] = {}
        self.categories_type_map: Dict[str, str] = {}
        if db_session:
            self._load_categories()
    
    def _load_categories(self):
        """Load categories for auto-classification"""
        if not self.db:
            return
        categories = self.db.query(Category).filter(Category.is_deleted == False).all()
        self.categories_map = {cat.name: cat.id for cat in categories}
        self.categories_type_map = {cat.name: cat.type for cat in categories}
    
    def process_image(self, image_content: bytes, provider: str = "auto") -> OCRResult:
        """
        Process image and extract transaction data
        
        Args:
            image_content: Image file bytes
            provider: OCR provider - "auto", "tesseract", "regex"
        
        Returns:
            OCRResult with extracted data
        """
        # Try providers in order
        if provider == "auto":
            # Try tesseract first, then regex
            try:
                return self._process_with_tesseract(image_content)
            except Exception:
                return self._process_with_regex(image_content)
        elif provider == "tesseract":
            return self._process_with_tesseract(image_content)
        else:
            return self._process_with_regex(image_content)
    
    def _process_with_tesseract(self, image_content: bytes) -> OCRResult:
        """Process image using Tesseract OCR"""
        try:
            import pytesseract
            from PIL import Image
        except ImportError:
            raise ImportError("pytesseract and Pillow are required for OCR. Install with: pip install pytesseract pillow")
        
        # Open image from bytes
        image = Image.open(io.BytesIO(image_content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Perform OCR
        raw_text = pytesseract.image_to_string(image, lang='chi_sim+eng')
        
        # Parse the extracted text
        return self._parse_text(raw_text, provider="tesseract")
    
    def _process_with_regex(self, image_content: bytes) -> OCRResult:
        """
        Regex-based parsing as fallback
        Uses simple text extraction patterns without actual OCR
        """
        # Try to extract text from image using basic patterns
        # This is a fallback when no OCR is available
        
        # For now, return empty result with low confidence
        # In production, this could try to decode common image formats
        return OCRResult(
            confidence=0.0,
            raw_text="",
            provider="regex"
        )
    
    def _parse_text(self, text: str, provider: str = "regex") -> OCRResult:
        """Parse OCR text to extract transaction data"""
        
        result = OCRResult(
            raw_text=text,
            provider=provider
        )
        
        # Extract amount
        amount = self._extract_amount(text)
        if amount:
            result.amount = amount
        
        # Extract date
        date = self._extract_date(text)
        if date:
            result.date = date
        
        # Extract merchant
        merchant = self._extract_merchant(text)
        if merchant:
            result.merchant = merchant
        
        # Auto-categorize
        category = self._auto_categorize(text)
        if category:
            result.category = category
        
        # Generate note
        note_parts = []
        if merchant:
            note_parts.append(merchant)
        if category:
            note_parts.append(category)
        if note_parts:
            result.note = " ".join(note_parts)
        
        # Determine transaction type (default to expense for receipts)
        result.type = "expense"
        
        # Calculate confidence based on what was extracted
        confidence = 0.0
        if result.amount:
            confidence += 0.4
        if result.date:
            confidence += 0.3
        if result.merchant or result.category:
            confidence += 0.3
        result.confidence = min(confidence, 1.0)
        
        return result
    
    def _extract_amount(self, text: str) -> Optional[Decimal]:
        """Extract amount from text using various patterns"""
        patterns = [
            # RMB patterns
            r'[合计小计实付应付总额共计]?[：:]?\s*[¥￥]?\s*(\d+(?:\.\d{1,2})?)\s*元?',
            r'[合计小计实付应付总额共计]?[：:]?\s*(\d+(?:\.\d{1,2})?)\s*',
            # Generic amount patterns
            r'(?:金额|付款|支付)[：:]?\s*[¥￥]?\s*(\d+(?:\.\d{1,2})?)\s*元?',
            r'(\d+\.\d{2})\s*元',
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    amount = Decimal(match)
                    if amount > 0 and amount < 1000000:  # Reasonable limits
                        amounts.append(amount)
                except:
                    continue
        
        if amounts:
            return max(amounts)
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text"""
        patterns = [
            # Date patterns
            r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)',
            r'(\d{4}\d{2}\d{2})',
            r'(\d{1,2}[-/月]\d{1,2}[日]?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                # Normalize date format
                date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')
                
                # Parse and validate
                try:
                    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d', '%m-%d', '%m/%d']:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            if dt.year == 1900:
                                # Likely a month-day only, use current year
                                dt = dt.replace(year=datetime.now().year)
                            return dt.strftime('%Y-%m-%d')
                        except:
                            continue
                except:
                    continue
        
        return None
    
    def _extract_merchant(self, text: str) -> Optional[str]:
        """Extract merchant name from text"""
        # Look for common merchant patterns
        lines = text.split('\n')
        
        # First few lines often contain merchant name
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 2 and len(line) < 30:
                # Skip lines that look like amounts or dates
                if not re.match(r'^[\d\s\-\/\.]+$', line):
                    # Skip common receipt headers
                    if any(skip in line for skip in ['小票', 'Receipt', '发票', '二维码', '电话', '地址']):
                        continue
                    return line
        
        return None
    
    def _auto_categorize(self, text: str) -> Optional[str]:
        """Auto-categorize based on keywords"""
        text_lower = text.lower()
        
        for cat_name, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return cat_name
        
        return None


# Singleton instance
_ocr_service: Optional[OCRService] = None


def get_ocr_service(db_session=None) -> OCRService:
    """Get OCR service singleton"""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService(db_session)
    else:
        _ocr_service.db = db_session
        _ocr_service._load_categories()
    return _ocr_service
