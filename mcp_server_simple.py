"""
Энгийн MCP Server (SDK шаардахгүй)
JSON-RPC протокол ашиглах
"""
import json
import sys
from database import db
from ai_agent import BusinessAIAgent
from config import config

# AI agent үүсгэх
agent = BusinessAIAgent(config.GEMINI_API_KEY)

def handle_request(request):
    """Request боловсруулах"""
    try:
        method = request.get("method", "")
        params = request.get("params", {})
        
        if method == "tools/list":
            return {
                "tools": [
                    {
                        "name": "get_sales_by_sku",
                        "description": "SKU-аар борлуулалтын мэдээлэл авах",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "sku_id": {"type": "integer"},
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"}
                            }
                        }
                    },
                    {
                        "name": "get_sales_by_merchant",
                        "description": "Merchant-аар борлуулалтын мэдээлэл авах",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "merchant_id": {"type": "integer"},
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"}
                            }
                        }
                    },
                    {
                        "name": "get_sales_by_district",
                        "description": "District-аар борлуулалтын мэдээлэл авах",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "district": {"type": "string"},
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"}
                            }
                        }
                    },
                    {
                        "name": "get_sales_by_time_period",
                        "description": "Цаг хугацааны дагуу борлуулалтын мэдээлэл авах",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "period": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"}
                            }
                        }
                    },
                    {
                        "name": "get_sales_rep_performance",
                        "description": "Sales rep-ийн гүйцэтгэлийн мэдээлэл авах",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "sales_rep_id": {"type": "integer"},
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"}
                            }
                        }
                    },
                    {
                        "name": "answer_business_question",
                        "description": "Байгалийн хэл дээрх бизнесийн асуултанд хариулах",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string"}
                            },
                            "required": ["question"]
                        }
                    }
                ]
            }
        
        elif method == "tools/call":
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            
            if tool_name == "get_sales_by_sku":
                result = db.get_sales_by_sku(
                    sku_id=arguments.get("sku_id"),
                    start_date=arguments.get("start_date"),
                    end_date=arguments.get("end_date")
                )
            elif tool_name == "get_sales_by_merchant":
                result = db.get_sales_by_merchant(
                    merchant_id=arguments.get("merchant_id"),
                    start_date=arguments.get("start_date"),
                    end_date=arguments.get("end_date")
                )
            elif tool_name == "get_sales_by_district":
                result = db.get_sales_by_district(
                    district=arguments.get("district"),
                    start_date=arguments.get("start_date"),
                    end_date=arguments.get("end_date")
                )
            elif tool_name == "get_sales_by_time_period":
                result = db.get_sales_by_time_period(
                    period=arguments.get("period", "daily"),
                    start_date=arguments.get("start_date"),
                    end_date=arguments.get("end_date")
                )
            elif tool_name == "get_sales_rep_performance":
                result = db.get_sales_rep_performance(
                    sales_rep_id=arguments.get("sales_rep_id"),
                    start_date=arguments.get("start_date"),
                    end_date=arguments.get("end_date")
                )
            elif tool_name == "answer_business_question":
                question = arguments.get("question", "")
                result = agent.answer(question)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2, default=str)
                    }
                ]
            }
        
        else:
            return {"error": f"Unknown method: {method}"}
    
    except Exception as e:
        return {"error": str(e)}

def main():
    """Main loop - stdin/stdout ашиглах"""
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = handle_request(request)
            
            # Response илгээх
            response_json = json.dumps(response)
            print(response_json, flush=True)
        
        except json.JSONDecodeError:
            error_response = {"error": "Invalid JSON"}
            print(json.dumps(error_response), flush=True)
        except Exception as e:
            error_response = {"error": str(e)}
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    main()

