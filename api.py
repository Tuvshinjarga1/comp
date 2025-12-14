"""
FastAPI backend for Retail Beverage AI Assistant
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from database import db
from ai_agent import BusinessAIAgent
from config import config
import json

app = FastAPI(title="Retail Beverage AI Assistant")

# CORS тохируулах
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler нэмэх
@app.exception_handler(ConnectionError)
async def connection_error_handler(request, exc):
    """Database холболтын алдааг боловсруулах"""
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=503,
        content={
            "status": "error",
            "message": f"Database холболт байхгүй байна: {str(exc)}",
            "detail": "Database серверийг шалгана уу. test_connection.py ажиллуулж шалгаарай."
        }
    )

# AI agent үүсгэх
agent = BusinessAIAgent(config.GEMINI_API_KEY)

# Request models
class QueryRequest(BaseModel):
    question: str

class SalesBySKURequest(BaseModel):
    sku_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class SalesByMerchantRequest(BaseModel):
    merchant_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class SalesByDistrictRequest(BaseModel):
    district: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class SalesByTimePeriodRequest(BaseModel):
    period: str = "daily"
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class SalesRepPerformanceRequest(BaseModel):
    sales_rep_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Retail Beverage AI Assistant API", "status": "running"}

@app.post("/api/query")
async def answer_query(request: QueryRequest):
    """Байгалийн хэл дээрх асуултанд хариулах"""
    try:
        response = agent.answer(request.question)
        return {"answer": response, "status": "success"}
    except ConnectionError as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Database холболт байхгүй байна: {str(e)}. Database серверийг шалгана уу."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sales/sku")
async def get_sales_by_sku(request: SalesBySKURequest):
    """SKU-аар борлуулалт"""
    try:
        result = db.get_sales_by_sku(
            sku_id=request.sku_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return {"data": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sales/merchant")
async def get_sales_by_merchant(request: SalesByMerchantRequest):
    """Merchant-аар борлуулалт"""
    try:
        result = db.get_sales_by_merchant(
            merchant_id=request.merchant_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return {"data": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sales/district")
async def get_sales_by_district(request: SalesByDistrictRequest):
    """District-аар борлуулалт"""
    try:
        result = db.get_sales_by_district(
            district=request.district,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return {"data": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sales/time-period")
async def get_sales_by_time_period(request: SalesByTimePeriodRequest):
    """Цаг хугацааны дагуу борлуулалт"""
    try:
        result = db.get_sales_by_time_period(
            period=request.period,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return {"data": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sales/sales-rep")
async def get_sales_rep_performance(request: SalesRepPerformanceRequest):
    """Sales rep гүйцэтгэл"""
    try:
        result = db.get_sales_rep_performance(
            sales_rep_id=request.sales_rep_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return {"data": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights/top-skus")
async def get_top_skus(limit: int = 10, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Top SKU-ууд"""
    try:
        result = db.get_top_skus(limit=limit, start_date=start_date, end_date=end_date)
        return {"data": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights/district-trends")
async def get_district_trends(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """District trends"""
    try:
        result = db.get_district_trends(start_date=start_date, end_date=end_date)
        return {"data": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights/category-summary")
async def get_category_summary(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Category summary"""
    try:
        result = db.get_category_summary(start_date=start_date, end_date=end_date)
        return {"data": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/insights/merchant-patterns")
async def get_merchant_patterns(merchant_id: Optional[int] = None):
    """Merchant ordering patterns"""
    try:
        result = db.get_merchant_ordering_patterns(merchant_id=merchant_id)
        return {"data": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Static files (HTML, CSS, JS)
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/chat", response_class=HTMLResponse)
async def chat_page():
    """Chat UI хуудас"""
    try:
        html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Static files not found</h1><p>Please ensure static/index.html exists</p>",
            status_code=404
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

