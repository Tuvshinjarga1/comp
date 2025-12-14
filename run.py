"""
Retail Beverage AI Assistant - Main entry point
"""
import uvicorn
from api import app

if __name__ == "__main__":
    print("🚀 Retail Beverage AI Assistant эхэлж байна...")
    print("📊 Database холболтыг шалгаж байна...")
    try:
        from database import db
        db._ensure_connection()
        if db._connected:
            print("✓ Database холбогдлоо")
        else:
            print("⚠ Database холбогдож чадсангүй. Query хийхэд алдаа гарч магадгүй.")
    except Exception as e:
        print(f"⚠ Database холболт: {e}")
    print("🌐 Web UI: http://localhost:8000/chat")
    print("📡 API: http://localhost:8000")
    print("\nЗогсоохын тулд Ctrl+C дараарай\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

