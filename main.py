import os
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


def _mock_quote(base: float):
    # Simulate a small percentage change
    pct = random.uniform(-3, 3)
    value = base * (1 + pct / 100)
    trend = "up" if pct >= 0 else "down"
    return f"{value:.2f}", f"{pct:+.2f}%", trend

@app.get("/api/market-data")
def market_data():
    """
    Mock market data for BSE stocks. In production, integrate with Alpha Vantage and Yahoo Finance
    using API keys provided via environment variables.
    """
    try:
        bases = {
            "reliance": ("💹 Reliance", 2450.0),
            "tcs": ("💻 TCS", 3860.0),
            "hdfc": ("🏦 HDFC Bank", 1460.0),
            "icici": ("🏦 ICICI Bank", 1020.0),
            "infy": ("🧠 Infosys", 1520.0),
            "hul": ("🧼 HUL", 2460.0),
            "sbi": ("🏛️ SBI", 610.0),
            "airtel": ("📡 Airtel", 1150.0),
            "bajaj": ("💳 Bajaj Finance", 7200.0),
            "lt": ("🏗️ L&T", 3450.0),
        }
        data = {}
        for key, (label, base) in bases.items():
            value, change, trend = _mock_quote(base)
            data[key] = {
                "symbol": label,
                "value": value,
                "change": change,
                "trend": trend,
            }
        return data
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
