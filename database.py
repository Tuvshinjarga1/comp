import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
load_dotenv()

class Database:
    def __init__(self):
        self.conn = None
        self._connected = False
    
    def _ensure_connection(self):
        """Холболт байгаа эсэхийг шалгаж, байхгүй бол холбогдох"""
        try:
            if self.conn is None:
                self.connect()
            elif hasattr(self.conn, 'closed') and self.conn.closed:
                self.connect()
        except Exception:
            # Холболт хийж чадсангүй, дараа query хийхэд алдаа өгнө
            pass
    
    def connect(self):
        """PostgreSQL холболт үүсгэх"""
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("DATABASE_HOST"),
                port=os.getenv("DATABASE_PORT"),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD"),
                database=os.getenv("DATABASE_NAME"),
                connect_timeout=5  # 5 секундын timeout
            )
            self._connected = True
            print("✓ Database холбогдлоо")
        except Exception as e:
            self._connected = False
            print(f"⚠ Database холболт алдаатай: {e}")
            print("⚠ Database холболтгүйгээр систем ажиллахгүй байж магадгүй.")
            # Холболтгүй байхад raise хийхгүй, зөвхөн query хийхэд алдаа өгөх
            self.conn = None
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """SQL query ажиллуулах"""
        self._ensure_connection()
        if self.conn is None:
            raise ConnectionError("Database холболт байхгүй байна. Database серверийг шалгана уу.")
        
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            print(f"Query алдаа: {e}")
            raise
    
    def get_sales_by_sku(self, sku_id: Optional[int] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """SKU-аар борлуулалт авах"""
        query = """
            SELECT 
                sku.id as sku_id,
                sku.name as sku_name,
                sku.category,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_sales,
                COALESCE(SUM(oi.quantity), 0) as total_quantity,
                COUNT(DISTINCT o.id) as order_count
            FROM sku
            LEFT JOIN order_items oi ON sku.id = oi.sku_id
            LEFT JOIN orders o ON oi.order_id = o.id
            WHERE 1=1
        """
        params = []
        
        if sku_id:
            query += " AND sku.id = %s"
            params.append(sku_id)
        
        if start_date:
            query += " AND o.order_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND o.order_date <= %s"
            params.append(end_date)
        
        query += " GROUP BY sku.id, sku.name, sku.category ORDER BY total_sales DESC"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_sales_by_merchant(self, merchant_id: Optional[int] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Merchant-аар борлуулалт авах"""
        query = """
            SELECT 
                m.id as merchant_id,
                m.name as merchant_name,
                m.district,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_sales,
                COALESCE(SUM(oi.quantity), 0) as total_quantity,
                COUNT(DISTINCT o.id) as order_count
            FROM merchants m
            LEFT JOIN orders o ON m.id = o.merchant_id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE 1=1
        """
        params = []
        
        if merchant_id:
            query += " AND m.id = %s"
            params.append(merchant_id)
        
        if start_date:
            query += " AND o.order_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND o.order_date <= %s"
            params.append(end_date)
        
        query += " GROUP BY m.id, m.name, m.district ORDER BY total_sales DESC"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_sales_by_district(self, district: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """District-аар борлуулалт авах"""
        query = """
            SELECT 
                m.district,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_sales,
                COALESCE(SUM(oi.quantity), 0) as total_quantity,
                COUNT(DISTINCT o.id) as order_count,
                COUNT(DISTINCT m.id) as merchant_count
            FROM merchants m
            LEFT JOIN orders o ON m.id = o.merchant_id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE 1=1
        """
        params = []
        
        if district:
            query += " AND m.district = %s"
            params.append(district)
        
        if start_date:
            query += " AND o.order_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND o.order_date <= %s"
            params.append(end_date)
        
        query += " GROUP BY m.district ORDER BY total_sales DESC"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_sales_by_time_period(self, period: str = "daily", start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Цаг хугацааны дагуу борлуулалт авах (daily/weekly/monthly)"""
        if period == "daily":
            date_format = "DATE(o.order_date)"
        elif period == "weekly":
            date_format = "DATE_TRUNC('week', o.order_date)"
        elif period == "monthly":
            date_format = "DATE_TRUNC('month', o.order_date)"
        else:
            date_format = "DATE(o.order_date)"
        
        query = f"""
            SELECT 
                {date_format} as period,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_sales,
                COALESCE(SUM(oi.quantity), 0) as total_quantity,
                COUNT(DISTINCT o.id) as order_count
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND o.order_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND o.order_date <= %s"
            params.append(end_date)
        
        query += f" GROUP BY {date_format} ORDER BY period DESC"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_sales_rep_performance(self, sales_rep_id: Optional[int] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Sales rep-ийн гүйцэтгэл авах"""
        query = """
            SELECT 
                sr.id as sales_rep_id,
                sr.name as sales_rep_name,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_sales,
                COALESCE(SUM(oi.quantity), 0) as total_quantity,
                COUNT(DISTINCT o.id) as order_count,
                COUNT(DISTINCT o.merchant_id) as merchant_count
            FROM sales_reps sr
            LEFT JOIN orders o ON sr.id = o.sales_rep_id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE 1=1
        """
        params = []
        
        if sales_rep_id:
            query += " AND sr.id = %s"
            params.append(sales_rep_id)
        
        if start_date:
            query += " AND o.order_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND o.order_date <= %s"
            params.append(end_date)
        
        query += " GROUP BY sr.id, sr.name ORDER BY total_sales DESC"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_top_skus(self, limit: int = 10, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Хамгийн их борлуулалттай SKU-ууд"""
        return self.get_sales_by_sku(start_date=start_date, end_date=end_date)[:limit]
    
    def get_district_trends(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """District-ийн чиг хандлага"""
        return self.get_sales_by_district(start_date=start_date, end_date=end_date)
    
    def get_category_summary(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Категори-ийн хураангуй"""
        query = """
            SELECT 
                sku.category,
                COALESCE(SUM(oi.quantity * oi.price), 0) as total_sales,
                COALESCE(SUM(oi.quantity), 0) as total_quantity,
                COUNT(DISTINCT o.id) as order_count,
                COUNT(DISTINCT sku.id) as sku_count
            FROM sku
            LEFT JOIN order_items oi ON sku.id = oi.sku_id
            LEFT JOIN orders o ON oi.order_id = o.id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND o.order_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND o.order_date <= %s"
            params.append(end_date)
        
        query += " GROUP BY sku.category ORDER BY total_sales DESC"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def get_merchant_ordering_patterns(self, merchant_id: Optional[int] = None) -> List[Dict]:
        """Merchant-ийн захиалгын хэв маяг"""
        query = """
            SELECT 
                m.id as merchant_id,
                m.name as merchant_name,
                DATE_TRUNC('month', o.order_date) as month,
                COUNT(DISTINCT o.id) as orders_per_month,
                COALESCE(SUM(oi.quantity * oi.price), 0) as monthly_sales
            FROM merchants m
            LEFT JOIN orders o ON m.id = o.merchant_id
            LEFT JOIN order_items oi ON o.id = oi.order_id
            WHERE 1=1
        """
        params = []
        
        if merchant_id:
            query += " AND m.id = %s"
            params.append(merchant_id)
        
        query += " GROUP BY m.id, m.name, DATE_TRUNC('month', o.order_date) ORDER BY m.id, month DESC"
        
        return self.execute_query(query, tuple(params) if params else None)
    
    def execute_custom_query(self, query: str) -> List[Dict]:
        """Custom SQL query ажиллуулах"""
        return self.execute_query(query)
    
    def close(self):
        """Холболт хаах"""
        if self.conn:
            self.conn.close()

# Global database instance (lazy connection)
db = Database()

