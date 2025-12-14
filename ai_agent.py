from typing import Dict, Any, Optional
from database import db
import google.generativeai as genai
import json
from datetime import datetime, timedelta
import re

class BusinessAIAgent:
    def __init__(self, api_key: str):
        # Gemini API тохируулах
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.system_prompt = """Та нь retail beverage ordering системийн бизнесийн мэдээлэл өгөх AI туслах юм.

Таны үүрэг:
1. Борлуулалтын мэдээлэл авах (SKU, merchant, district, цаг хугацаа, sales rep)
2. Insights үүсгэх (top SKU, trends, patterns)
3. Байгалийн хэл дээрх асуултуудад хариулах

Асуултуудыг шинжилж, зөв database query-г сонгох хэрэгтэй."""

    def parse_query(self, user_query: str) -> Dict[str, Any]:
        """Хэрэглэгчийн асуултыг шинжлэх"""
        query_lower = user_query.lower()
        
        # Query төрөл тодорхойлох
        query_type = None
        filters = {}
        
        # SKU асуулт
        if any(word in query_lower for word in ['sku', 'бүтээгдэхүүн', 'product', 'item']):
            query_type = "sku"
            # SKU ID эсвэл нэр олох
            sku_match = re.search(r'sku[:\s]+(\d+)', query_lower)
            if sku_match:
                filters['sku_id'] = int(sku_match.group(1))
        
        # Merchant асуулт
        if any(word in query_lower for word in ['merchant', 'худалдаачин', 'client', 'customer']):
            query_type = "merchant"
            merchant_match = re.search(r'merchant[:\s]+(\d+)', query_lower)
            if merchant_match:
                filters['merchant_id'] = int(merchant_match.group(1))
        
        # District асуулт
        if any(word in query_lower for word in ['district', 'бүс', 'region', 'area']):
            query_type = "district"
            # District нэр олох
            district_match = re.search(r'district[:\s]+([a-zа-я\s]+)', query_lower, re.IGNORECASE)
            if district_match:
                filters['district'] = district_match.group(1).strip()
        
        # Time period асуулт
        if any(word in query_lower for word in ['day', 'week', 'month', 'өдөр', 'долоо хоног', 'сар']):
            if 'daily' in query_lower or 'өдөр' in query_lower:
                query_type = "time_period"
                filters['period'] = "daily"
            elif 'week' in query_lower or 'долоо хоног' in query_lower:
                query_type = "time_period"
                filters['period'] = "weekly"
            elif 'month' in query_lower or 'сар' in query_lower:
                query_type = "time_period"
                filters['period'] = "monthly"
        
        # Sales rep асуулт
        if any(word in query_lower for word in ['sales rep', 'rep', 'төлөөлөгч', 'salesperson']):
            query_type = "sales_rep"
            rep_match = re.search(r'rep[:\s]+(\d+)', query_lower)
            if rep_match:
                filters['sales_rep_id'] = int(rep_match.group(1))
        
        # Top/Insights асуулт
        if any(word in query_lower for word in ['top', 'best', 'highest', 'дээд', 'хамгийн']):
            if 'sku' in query_lower:
                query_type = "top_skus"
            elif 'district' in query_lower or 'trend' in query_lower:
                query_type = "district_trends"
            elif 'category' in query_lower:
                query_type = "category_summary"
        
        # Date range олох
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        dates = re.findall(date_pattern, user_query)
        if len(dates) >= 2:
            filters['start_date'] = dates[0]
            filters['end_date'] = dates[1]
        elif len(dates) == 1:
            filters['start_date'] = dates[0]
        
        # Хэрэв тодорхойлогдоогүй бол LLM ашиглах
        if not query_type:
            query_type = self._classify_with_llm(user_query)
        
        return {
            'type': query_type,
            'filters': filters,
            'original_query': user_query
        }
    
    def _classify_with_llm(self, query: str) -> str:
        """LLM ашиглан query төрөл тодорхойлох"""
        prompt = f"""Дараах асуултыг шинжилж, query төрлийг тодорхойл:
        
Асуулт: {query}

Боломжит төрлүүд:
- sku: SKU-тай холбоотой
- merchant: Merchant-тай холбоотой
- district: District-тай холбоотой
- time_period: Цаг хугацаатай холбоотой
- sales_rep: Sales rep-тай холбоотой
- top_skus: Top SKU авах
- district_trends: District trends
- category_summary: Category summary

Зөвхөн төрлийн нэрийг хариул (жишээ: sku)"""
        
        try:
            response = self.model.generate_content(prompt)
            # Gemini response-ийг авах
            if hasattr(response, 'text') and response.text:
                return response.text.strip().lower()
            elif hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].content.parts[0].text.strip().lower()
            return "general"
        except Exception as e:
            print(f"Gemini API алдаа: {e}")
            return "general"
    
    def execute_query(self, parsed_query: Dict[str, Any]) -> Any:
        """Query ажиллуулах"""
        query_type = parsed_query['type']
        filters = parsed_query['filters']
        
        try:
            if query_type == "sku":
                return db.get_sales_by_sku(
                    sku_id=filters.get('sku_id'),
                    start_date=filters.get('start_date'),
                    end_date=filters.get('end_date')
                )
            elif query_type == "merchant":
                return db.get_sales_by_merchant(
                    merchant_id=filters.get('merchant_id'),
                    start_date=filters.get('start_date'),
                    end_date=filters.get('end_date')
                )
            elif query_type == "district":
                return db.get_sales_by_district(
                    district=filters.get('district'),
                    start_date=filters.get('start_date'),
                    end_date=filters.get('end_date')
                )
            elif query_type == "time_period":
                return db.get_sales_by_time_period(
                    period=filters.get('period', 'daily'),
                    start_date=filters.get('start_date'),
                    end_date=filters.get('end_date')
                )
            elif query_type == "sales_rep":
                return db.get_sales_rep_performance(
                    sales_rep_id=filters.get('sales_rep_id'),
                    start_date=filters.get('start_date'),
                    end_date=filters.get('end_date')
                )
            elif query_type == "top_skus":
                return db.get_top_skus(
                    limit=10,
                    start_date=filters.get('start_date'),
                    end_date=filters.get('end_date')
                )
            elif query_type == "district_trends":
                return db.get_district_trends(
                    start_date=filters.get('start_date'),
                    end_date=filters.get('end_date')
                )
            elif query_type == "category_summary":
                return db.get_category_summary(
                    start_date=filters.get('start_date'),
                    end_date=filters.get('end_date')
                )
            else:
                # Custom query эсвэл general асуулт
                return self._handle_general_query(parsed_query)
        except Exception as e:
            return {"error": str(e)}
    
    def _handle_general_query(self, parsed_query: Dict[str, Any]) -> Any:
        """Ерөнхий асуултыг боловсруулах"""
        # LLM ашиглан SQL query үүсгэх эсвэл бусад query ажиллуулах
        return {"message": "Энэ төрлийн асуултыг одоогоор дэмжихгүй байна"}
    
    def format_response(self, data: Any, query_type: str) -> str:
        """Хариуг форматлах"""
        if isinstance(data, dict) and 'error' in data:
            return f"Алдаа гарлаа: {data['error']}"
        
        if not data:
            return "Мэдээлэл олдсонгүй."
        
        # LLM ашиглан хариуг форматлах
        full_prompt = f"""{self.system_prompt}

Дараах database query-ийн үр дүнг хэрэглэгчид ойлгомжтой хэлбэрээр тайлбарла:

Query төрөл: {query_type}
Үр дүн: {json.dumps(data, indent=2, default=str)}

Хариуг Монгол хэлээр, товч, ойлгомжтой байлга. Тоон мэдээлэл, харьцуулалт, insights оруул."""
        
        try:
            response = self.model.generate_content(full_prompt)
            # Gemini response-ийг авах
            if hasattr(response, 'text') and response.text:
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].content.parts[0].text
            # Fallback формат
            return json.dumps(data, indent=2, default=str)
        except Exception as e:
            print(f"Gemini API алдаа: {e}")
            # Fallback формат
            return json.dumps(data, indent=2, default=str)
    
    def answer(self, user_query: str) -> str:
        """Асуултанд хариулах"""
        # Query шинжлэх
        parsed_query = self.parse_query(user_query)
        
        # Query ажиллуулах
        data = self.execute_query(parsed_query)
        
        # Хариуг форматлах
        response = self.format_response(data, parsed_query['type'])
        
        return response

