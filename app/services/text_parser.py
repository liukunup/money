"""
Text parsing service for extracting transaction data from various text formats.
Supports Alipay SMS, WeChat Pay, and plain text formats.
"""
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


@dataclass
class ParsedTransaction:
    """Parsed transaction data"""
    amount: Optional[Decimal] = None
    date: Optional[date] = None
    category: Optional[str] = None
    merchant: Optional[str] = None
    note: Optional[str] = None
    type: str = "expense"
    confidence: float = 0.0
    raw_text: str = ""
    format_type: str = "unknown"


# Category keywords mapping
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "餐饮": ["餐厅", "饭店", "麦当劳", "肯德基", "外卖", "火锅", "烧烤", "咖啡", "奶茶", "早餐", "午餐", "晚餐", "食堂", "面馆", "快餐"],
    "交通": ["地铁", "公交", "出租车", "滴滴", "打车", "高铁", "火车", "飞机", "机票", "加油", "停车", "ETC"],
    "购物": ["淘宝", "天猫", "京东", "拼多多", "苏宁", "国美", "超市", "便利店", "商场", "百货"],
    "娱乐": ["电影", "KTV", "网吧", "游戏", "演出", "演唱会", "展览", "博物馆", "公园", "游乐场"],
    "住房": ["房租", "水电", "燃气", "物业", "中介", "维修"],
    "医疗": ["医院", "药店", "诊所", "体检", "牙科", "眼科"],
    "教育": ["学费", "培训", "辅导", "书籍", "文具", "教育"],
    "通讯": ["手机", "话费", "流量", "宽带", "广电"],
    "工资": ["工资", "薪资", "退休金", "养老金"],
    "奖金": ["奖金", "分红", "提成", "佣金"],
    "投资": ["理财", "股票", "基金", "债券", "收益"],
    "兼职": ["兼职", "外快", "副业"],
}


def parse_amount(text: str) -> Optional[Decimal]:
    """Extract amount from text using various patterns"""
    patterns = [
        # Alipay/WeChat patterns
        r"[\u4e00-\u9fa5]?[:：]?\s*(\d+(?:\.\d{1,2})?)\s*元",
        # Amount with currency symbol
        r"[$￥¥](\d+(?:\.\d{1,2})?)",
        # Plain number with optional currency
        r"(?:消费|支付|金额|付款|收款|入账)[:：]?\s*(\d+(?:\.\d{1,2})?)",
        # Standalone amount
        r"(\d+(?:\.\d{1,2})?)\s*(?:元|rmb)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                amount_str = match.group(1)
                # Handle Chinese numbers
                amount_str = convert_chinese_numbers(amount_str)
                return Decimal(amount_str)
            except (ValueError, AttributeError):
                continue
    
    return None


def convert_chinese_numbers(text: str) -> str:
    """Convert Chinese numbers to Arabic numbers"""
    # Handle common Chinese number words
    chinese_to_arabic = {
        "零": "0", "一": "1", "二": "2", "三": "3", "四": "4",
        "五": "5", "六": "6", "七": "7", "八": "8", "九": "9",
        "十": "10", "百": "100", "千": "1000",
    }
    
    result = text
    for cn, ar in chinese_to_arabic.items():
        result = result.replace(cn, ar)
    
    return result


def parse_date(text: str) -> Optional[date]:
    """Extract date from text"""
    today = date.today()
    
    # Check for relative dates
    relative_patterns = [
        (r"今天", lambda: today),
        (r"昨天", lambda: date(today.year, today.month, today.day - 1) if today.day > 1 else date(today.year, today.month - 1, 28) if today.month > 1 else date(today.year - 1, 12, 28)),
        (r"前天", lambda: date(today.year, today.month, today.day - 2) if today.day > 2 else date(today.year, today.month - 1, 27) if today.month > 1 else date(today.year - 1, 12, 27)),
        (r"(\d+)天前", lambda m: date(today.year, today.month, today.day - int(m.group(1))) if today.day > int(m.group(1)) else date(today.year, today.month - 1, 28) if today.month > 1 else date(today.year - 1, 12, 28)),
    ]
    
    for pattern, resolver in relative_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return resolver() if not callable(resolver) else resolver(match)
            except:
                continue
    
    # Check for absolute dates
    date_patterns = [
        # YYYY-MM-DD or YYYY/MM/DD
        r"(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})",
        # MM-DD or MM/DD
        r"(?:今天|昨日)?(\d{1,2})[-/月](\d{1,2})",
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                groups = match.groups()
                if len(groups) == 3 and len(groups[0]) == 4:
                    # YYYY-MM-DD
                    return date(int(groups[0]), int(groups[1]), int(groups[2]))
                elif len(groups) == 2:
                    # MM-DD, assume current year
                    month, day = int(groups[0]), int(groups[1])
                    # Handle year boundary
                    if month > today.month:
                        return date(today.year - 1, month, day)
                    return date(today.year, month, day)
            except (ValueError, AttributeError):
                continue
    
    return None


def parse_category(text: str) -> Optional[str]:
    """Extract category from text based on keywords"""
    text_lower = text.lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return category
    
    return None


def parse_merchant(text: str) -> Optional[str]:
    """Extract merchant/store name from text"""
    # Alipay pattern
    alipay_match = re.search(r"(?:商户|商家)[:：]\s*([^\s\n]{2,20})", text)
    if alipay_match:
        return alipay_match.group(1).strip()
    
    # WeChat pattern
    wechat_match = re.search(r"(?:商户名|收款方)[:：]\s*([^\s\n]{2,20})", text)
    if wechat_match:
        return wechat_match.group(1).strip()
    
    # Common merchant patterns in plain text
    merchant_patterns = [
        r"在([^\s]{2,10})(?:店|餐厅|超市|商场|公司)",
        r"([^\s]{2,10})(?:消费|支付|花了)",
    ]
    
    for pattern in merchant_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    return None


def detect_format_type(text: str) -> str:
    """Detect the format type of the text"""
    if "支付宝" in text or "【支付宝】" in text:
        return "alipay"
    elif "微信支付" in text or "微信支付凭证" in text:
        return "wechat"
    elif re.search(r"\[.{2,10}\]", text):  # SMS format with brackets
        return "sms"
    else:
        return "plain"


def parse_alipay_sms(text: str) -> ParsedTransaction:
    """Parse Alipay SMS format"""
    result = ParsedTransaction(
        raw_text=text,
        format_type="alipay",
        type="expense"
    )
    
    # Extract amount
    result.amount = parse_amount(text)
    
    # Extract date
    result.date = parse_date(text)
    
    # Extract merchant (often in SMS)
    result.merchant = parse_merchant(text)
    
    # Build note from available info
    note_parts = []
    if result.merchant:
        note_parts.append(result.merchant)
    
    # Try to get more context from SMS
    if "消费" in text:
        match = re.search(r"消费\d+\.?\d*元", text)
        if match:
            note_parts.append(match.group())
    elif "收款" in text:
        result.type = "income"
        match = re.search(r"收款\d+\.?\d*元", text)
        if match:
            note_parts.append(match.group())
    
    if note_parts:
        result.note = " ".join(note_parts)
    
    # Calculate confidence
    confidence = 0.0
    if result.amount:
        confidence += 0.4
    if result.date:
        confidence += 0.3
    if result.merchant or result.note:
        confidence += 0.3
    result.confidence = min(confidence, 1.0)
    
    return result


def parse_wechat_pay(text: str) -> ParsedTransaction:
    """Parse WeChat Pay receipt format"""
    result = ParsedTransaction(
        raw_text=text,
        format_type="wechat",
        type="expense"
    )
    
    # Extract amount
    result.amount = parse_amount(text)
    
    # Extract date
    result.date = parse_date(text)
    
    # Extract merchant
    result.merchant = parse_merchant(text)
    
    # Build note
    note_parts = []
    if result.merchant:
        note_parts.append(result.merchant)
    
    if "支付" in text:
        note_parts.append("微信支付")
    
    if note_parts:
        result.note = " ".join(note_parts)
    
    # Check for income (red envelope, transfer received)
    if "收款" in text or "红包" in text or "转账" in text and "收款" in text:
        result.type = "income"
    
    # Calculate confidence
    confidence = 0.0
    if result.amount:
        confidence += 0.4
    if result.date:
        confidence += 0.3
    if result.merchant or result.note:
        confidence += 0.3
    result.confidence = min(confidence, 1.0)
    
    return result


def parse_plain_text(text: str) -> ParsedTransaction:
    """Parse plain text format"""
    result = ParsedTransaction(
        raw_text=text,
        format_type="plain",
        type="expense"
    )
    
    # Extract amount
    result.amount = parse_amount(text)
    
    # Extract date
    result.date = parse_date(text)
    
    # Extract category
    result.category = parse_category(text)
    
    # Extract merchant
    result.merchant = parse_merchant(text)
    
    # Try to detect if income
    income_keywords = ["收到", "收入", "工资", "奖金", "转账", "收款", "红包"]
    for keyword in income_keywords:
        if keyword in text:
            result.type = "income"
            break
    
    # Build note from remaining text
    note_parts = []
    if result.merchant:
        note_parts.append(result.merchant)
    if result.category:
        note_parts.append(result.category)
    
    # Add any remaining meaningful text
    cleaned_text = text
    for pattern in [r"\d+\.?\d*元?", r"今天|昨天|前天|\d+天前", r"\d{4}[-/年]\d{1,2}[-/月]\d{1,2}"]:
        cleaned_text = re.sub(pattern, "", cleaned_text)
    cleaned_text = cleaned_text.strip("：:、,\n ")
    if cleaned_text and len(cleaned_text) < 50:
        if result.note:
            result.note = f"{result.note} - {cleaned_text}"
        else:
            result.note = cleaned_text
    
    if note_parts and result.note:
        pass  # Keep combined note
    elif not result.note and note_parts:
        result.note = " ".join(note_parts)
    
    # Calculate confidence
    confidence = 0.0
    if result.amount:
        confidence += 0.4
    if result.date:
        confidence += 0.2
    if result.category:
        confidence += 0.2
    if result.merchant or result.note:
        confidence += 0.2
    result.confidence = min(confidence, 1.0)
    
    return result


def parse_text(text: str) -> ParsedTransaction:
    """
    Main entry point for parsing text.
    Automatically detects format and extracts transaction data.
    """
    if not text or not text.strip():
        return ParsedTransaction(
            raw_text=text or "",
            format_type="unknown",
            confidence=0.0
        )
    
    text = text.strip()
    format_type = detect_format_type(text)
    
    if format_type == "alipay":
        return parse_alipay_sms(text)
    elif format_type == "wechat":
        return parse_wechat_pay(text)
    else:
        return parse_plain_text(text)


def to_dict(parsed: ParsedTransaction) -> Dict[str, Any]:
    """Convert ParsedTransaction to dictionary for API response"""
    return {
        "amount": str(parsed.amount) if parsed.amount else None,
        "date": parsed.date.isoformat() if parsed.date else None,
        "category": parsed.category,
        "merchant": parsed.merchant,
        "note": parsed.note,
        "type": parsed.type,
        "confidence": parsed.confidence,
        "format_type": parsed.format_type,
    }
