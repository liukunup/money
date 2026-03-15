"""
AI Classification Service
- OpenAI-compatible interface
- Priority-based fallback strategy
- Keyword-based classification fallback
"""
import json
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

import httpx

from app.models.ai_provider import AIProvider
from app.models.category import Category

logger = logging.getLogger(__name__)


# Default classification prompt
CLASSIFICATION_PROMPT = """你是一个智能支出分类助手。根据用户提供的交易信息（金额、备注），判断这应该属于哪个分类。

可用分类：
{categories}

交易信息：
- 金额: {amount}
- 类型: {transaction_type}
- 备注: {note}

请根据以下JSON格式返回分类建议：
{{
    "category_id": 分类ID,
    "confidence": 置信度(0-1),
    "reason": "分类理由"
}}

注意：只返回JSON，不要其他内容。"""


class AIService:
    """AI Classification Service with fallback support"""
    
    def __init__(self, db: Session):
        self.db = db
        self._providers: Optional[List[AIProvider]] = None
    
    def _get_active_providers(self) -> List[AIProvider]:
        """Get all active providers sorted by priority"""
        if self._providers is None:
            self._providers = self.db.query(AIProvider).filter(
                AIProvider.is_active == True
            ).order_by(AIProvider.priority.asc()).all()
        return self._providers
    
    def _refresh_providers(self):
        """Refresh provider cache"""
        self._providers = None
    
    async def _call_provider(
        self,
        provider: AIProvider,
        messages: List[Dict[str, str]],
        model: str = None
    ) -> Optional[str]:
        """Call a single AI provider with OpenAI-compatible API"""
        try:
            models = json.loads(provider.models) if provider.models else ["gpt-3.5-turbo"]
            selected_model = model or models[0]
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Add API key to headers if present
            if provider.api_key:
                if provider.provider_type == "openai":
                    headers["Authorization"] = f"Bearer {provider.api_key}"
                elif provider.provider_type == "anthropic":
                    headers["x-api-key"] = provider.api_key
                elif provider.provider_type in ["deepseek", "moonshot", "zhipu", "minimax", "qianwen", "tongyi"]:
                    headers["Authorization"] = f"Bearer {provider.api_key}"
            
            payload = {
                "model": selected_model,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{provider.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.warning(
                        f"Provider {provider.name} returned {response.status_code}: {response.text}"
                    )
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling provider {provider.name}: {str(e)}")
            return None
    
    async def _call_with_fallback(
        self,
        messages: List[Dict[str, str]],
        model: str = None
    ) -> Optional[str]:
        """Try providers in priority order, fallback on failure"""
        providers = self._get_active_providers()
        
        if not providers:
            logger.warning("No active AI providers configured")
            return None
        
        for provider in providers:
            logger.info(f"Trying AI provider: {provider.name} (priority: {provider.priority})")
            result = await self._call_provider(provider, messages, model)
            if result:
                return result
            logger.info(f"Falling back to next provider...")
        
        return None
    
    async def classify_transaction(
        self,
        amount: float,
        transaction_type: str,
        note: str,
        categories: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Classify a transaction using AI, with fallback to keyword matching"""
        
        # First try AI classification
        category_list = "\n".join([
            f"- ID: {c['id']}, 名称: {c['name']}" 
            for c in categories
        ])
        
        prompt = CLASSIFICATION_PROMPT.format(
            categories=category_list,
            amount=amount,
            transaction_type=transaction_type,
            note=note or "无备注"
        )
        
        messages = [
            {"role": "system", "content": "你是一个专业的支出分类助手。"},
            {"role": "user", "content": prompt}
        ]
        
        result = await self._call_with_fallback(messages)
        
        if result:
            try:
                # Try to parse JSON from response
                # Handle potential markdown code blocks
                result = result.strip()
                if result.startswith("```json"):
                    result = result[7:]
                elif result.startswith("```"):
                    result = result[3:]
                if result.endswith("```"):
                    result = result[:-3]
                
                parsed = json.loads(result.strip())
                
                # Validate category_id exists
                category_ids = [c['id'] for c in categories]
                if parsed.get('category_id') in category_ids:
                    return parsed
                    
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse AI response: {e}")
        
        # Fallback to keyword-based classification
        return self._keyword_classify(amount, transaction_type, note, categories)
    
    def _keyword_classify(
        self,
        amount: float,
        transaction_type: str,
        note: str,
        categories: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Simple keyword-based classification fallback"""
        
        # Keyword mappings for common Chinese expense categories
        keyword_map = {
            # 餐饮
            "餐饮": ["餐厅", "饭店", "外卖", "快餐", "火锅", "烧烤", "披萨", "汉堡", "咖啡", "奶茶", "饮料", "早餐", "午餐", "晚餐", "麦当劳", "肯德基", "星巴克", "瑞幸", "美团", "饿了么"],
            # 交通
            "交通": ["地铁", "公交", "打车", "出租车", "滴滴", "高铁", "火车", "飞机", "加油", "停车", "过路费", "打车", "共享单车", "租车"],
            # 购物
            "购物": ["淘宝", "京东", "天猫", "拼多多", "唯品会", "苏宁", "国美", "亚马逊", "超市", "商场", "便利店", "网购", "快递"],
            # 娱乐
            "娱乐": ["电影", "KTV", "网吧", "游戏", "演出", "音乐会", "展览", "旅游", "酒店", "民宿", "门票", "健身房", "游泳", "篮球", "足球", "羽毛球"],
            # 住房
            "住房": ["房租", "水电费", "物业费", "燃气费", "宽带", "电话费", "暖气费", "维修", "装修"],
            # 医疗
            "医疗": ["医院", "药店", "诊所", "体检", "牙科", "眼科", "门诊", "药", "医保"],
            # 教育
            "教育": ["学费", "培训", "辅导", "书", "文具", "教育", "课程", "考试", "培训"],
            # 工资
            "工资": ["工资", "薪资", "月薪", "奖金", "年终奖", "补贴"],
            # 投资
            "投资": ["股票", "基金", "理财", "债券", "黄金", "比特币", "分红", "利息", "收益"],
            # 兼职
            "兼职": ["兼职", "外快", "副业", "接单", "私活"]
        }
        
        if not note:
            return None
        
        note_lower = note.lower()
        
        # Match keywords to categories
        for category in categories:
            category_name = category.get('name', '')
            keywords = keyword_map.get(category_name, [])
            
            for keyword in keywords:
                if keyword in note:
                    return {
                        "category_id": category['id'],
                        "confidence": 0.6,
                        "reason": f"关键词匹配: {keyword}"
                    }
        
        # Default category for unmatched transactions
        for category in categories:
            if transaction_type == "expense" and category.get('name') == "其他":
                return {
                    "category_id": category['id'],
                    "confidence": 0.3,
                    "reason": "默认分类为'其他'"
                }
            elif transaction_type == "income" and category.get('name') == "其他收入":
                return {
                    "category_id": category['id'],
                    "confidence": 0.3,
                    "reason": "默认分类为'其他收入'"
                }
        
        return None
    
    async def get_suggestions(
        self,
        note: str,
        categories: List[Dict[str, Any]],
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get multiple category suggestions for a note"""
        
        category_list = "\n".join([
            f"- ID: {c['id']}, 名称: {c['name']}" 
            for c in categories
        ])
        
        prompt = f"""根据以下交易备注，给出最可能的{limit}个分类建议：

可用分类：
{category_list}

备注: {note}

请按可能性从高到低排序，返回JSON数组格式：
[{{"category_id": 1, "reason": "理由1"}}, {{"category_id": 2, "reason": "理由2"}}]

只返回JSON数组。"""
        
        messages = [
            {"role": "system", "content": "你是一个智能分类助手。"},
            {"role": "user", "content": prompt}
        ]
        
        result = await self._call_with_fallback(messages)
        
        if result:
            try:
                # Clean response
                result = result.strip()
                if result.startswith("```json"):
                    result = result[7:]
                elif result.startswith("```"):
                    result = result[3:]
                if result.endswith("```"):
                    result = result[:-3]
                
                suggestions = json.loads(result.strip())
                
                # Validate category_ids
                category_ids = [c['id'] for c in categories]
                valid_suggestions = [
                    s for s in suggestions 
                    if s.get('category_id') in category_ids
                ]
                
                return valid_suggestions[:limit]
                
            except (json.JSONDecodeError, IndexError) as e:
                logger.warning(f"Failed to parse suggestions: {e}")
        
        # Fallback to keyword matching
        return self._keyword_suggestions(note, categories, limit)
    
    def _keyword_suggestions(
        self,
        note: str,
        categories: List[Dict[str, Any]],
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get keyword-based suggestions"""
        
        keyword_map = {
            "餐饮": ["餐厅", "饭店", "外卖", "快餐", "火锅", "烧烤", "披萨", "汉堡", "咖啡", "奶茶", "饮料", "早餐", "午餐", "晚餐", "麦当劳", "肯德基", "星巴克", "瑞幸"],
            "交通": ["地铁", "公交", "打车", "出租车", "滴滴", "高铁", "火车", "飞机", "加油", "停车", "过路费", "共享单车"],
            "购物": ["淘宝", "京东", "天猫", "拼多多", "唯品会", "超市", "商场", "便利店", "网购"],
            "娱乐": ["电影", "KTV", "网吧", "游戏", "演出", "音乐会", "展览", "旅游", "酒店", "健身房"],
            "住房": ["房租", "水电费", "物业费", "燃气费", "宽带", "电话费", "暖气费"],
            "医疗": ["医院", "药店", "诊所", "体检", "牙科", "眼科", "药"],
            "教育": ["学费", "培训", "辅导", "书", "文具", "课程"],
            "工资": ["工资", "薪资", "月薪", "奖金", "年终奖"],
            "投资": ["股票", "基金", "理财", "债券", "黄金", "分红", "利息"],
            "兼职": ["兼职", "外快", "副业", "接单"]
        }
        
        if not note:
            return []
        
        matches = []
        note_lower = note.lower()
        
        for category in categories:
            category_name = category.get('name', '')
            keywords = keyword_map.get(category_name, [])
            
            for keyword in keywords:
                if keyword in note:
                    matches.append({
                        "category_id": category['id'],
                        "reason": f"关键词: {keyword}"
                    })
                    break
        
        return matches[:limit]


# Service factory
def get_ai_service(db: Session) -> AIService:
    """Get AI service instance"""
    return AIService(db)
