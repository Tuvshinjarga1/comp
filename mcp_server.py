"""
MCP Server for Retail Beverage Ordering System
Model Context Protocol сервер
"""
import asyncio
import json
from typing import Any, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from database import db
from ai_agent import BusinessAIAgent
from config import config

# MCP сервер үүсгэх
server = Server("retail-beverage-assistant")

# AI agent үүсгэх
agent = BusinessAIAgent(config.GEMINI_API_KEY)

@server.list_tools()
async def list_tools() -> list[Tool]:
    """Боломжтой tool-уудыг жагсаах"""
    return [
        Tool(
            name="get_sales_by_sku",
            description="SKU-аар борлуулалтын мэдээлэл авах",
            inputSchema={
                "type": "object",
                "properties": {
                    "sku_id": {"type": "integer", "description": "SKU ID (optional)"},
                    "start_date": {"type": "string", "description": "Эхлэх огноо (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "Дуусах огноо (YYYY-MM-DD)"}
                }
            }
        ),
        Tool(
            name="get_sales_by_merchant",
            description="Merchant-аар борлуулалтын мэдээлэл авах",
            inputSchema={
                "type": "object",
                "properties": {
                    "merchant_id": {"type": "integer", "description": "Merchant ID (optional)"},
                    "start_date": {"type": "string", "description": "Эхлэх огноо (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "Дуусах огноо (YYYY-MM-DD)"}
                }
            }
        ),
        Tool(
            name="get_sales_by_district",
            description="District-аар борлуулалтын мэдээлэл авах",
            inputSchema={
                "type": "object",
                "properties": {
                    "district": {"type": "string", "description": "District нэр (optional)"},
                    "start_date": {"type": "string", "description": "Эхлэх огноо (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "Дуусах огноо (YYYY-MM-DD)"}
                }
            }
        ),
        Tool(
            name="get_sales_by_time_period",
            description="Цаг хугацааны дагуу борлуулалтын мэдээлэл авах",
            inputSchema={
                "type": "object",
                "properties": {
                    "period": {"type": "string", "enum": ["daily", "weekly", "monthly"], "description": "Хугацаа"},
                    "start_date": {"type": "string", "description": "Эхлэх огноо (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "Дуусах огноо (YYYY-MM-DD)"}
                }
            }
        ),
        Tool(
            name="get_sales_rep_performance",
            description="Sales rep-ийн гүйцэтгэлийн мэдээлэл авах",
            inputSchema={
                "type": "object",
                "properties": {
                    "sales_rep_id": {"type": "integer", "description": "Sales rep ID (optional)"},
                    "start_date": {"type": "string", "description": "Эхлэх огноо (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "Дуусах огноо (YYYY-MM-DD)"}
                }
            }
        ),
        Tool(
            name="get_top_skus",
            description="Хамгийн их борлуулалттай SKU-ууд",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Хэмжээ (default: 10)"},
                    "start_date": {"type": "string", "description": "Эхлэх огноо (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "Дуусах огноо (YYYY-MM-DD)"}
                }
            }
        ),
        Tool(
            name="get_district_trends",
            description="District-ийн чиг хандлага",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Эхлэх огноо (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "Дуусах огноо (YYYY-MM-DD)"}
                }
            }
        ),
        Tool(
            name="get_category_summary",
            description="Категори-ийн хураангуй",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Эхлэх огноо (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "Дуусах огноо (YYYY-MM-DD)"}
                }
            }
        ),
        Tool(
            name="answer_business_question",
            description="Байгалийн хэл дээрх бизнесийн асуултанд хариулах",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "Бизнесийн асуулт"}
                },
                "required": ["question"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Tool дуудах"""
    try:
        if name == "get_sales_by_sku":
            result = db.get_sales_by_sku(
                sku_id=arguments.get("sku_id"),
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date")
            )
        elif name == "get_sales_by_merchant":
            result = db.get_sales_by_merchant(
                merchant_id=arguments.get("merchant_id"),
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date")
            )
        elif name == "get_sales_by_district":
            result = db.get_sales_by_district(
                district=arguments.get("district"),
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date")
            )
        elif name == "get_sales_by_time_period":
            result = db.get_sales_by_time_period(
                period=arguments.get("period", "daily"),
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date")
            )
        elif name == "get_sales_rep_performance":
            result = db.get_sales_rep_performance(
                sales_rep_id=arguments.get("sales_rep_id"),
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date")
            )
        elif name == "get_top_skus":
            result = db.get_top_skus(
                limit=arguments.get("limit", 10),
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date")
            )
        elif name == "get_district_trends":
            result = db.get_district_trends(
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date")
            )
        elif name == "get_category_summary":
            result = db.get_category_summary(
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date")
            )
        elif name == "answer_business_question":
            question = arguments.get("question", "")
            result = agent.answer(question)
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]

async def main():
    """MCP серверийг ажиллуулах"""
    try:
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except ImportError:
        print("MCP SDK суугаагүй байна. 'pip install mcp' ажиллуулна уу.")
    except Exception as e:
        print(f"MCP сервер алдаа: {e}")

if __name__ == "__main__":
    asyncio.run(main())

