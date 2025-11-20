# optionchain-service/main.py
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI(title="optionchain-service")

@app.get("/optionchain")
async def optionchain(symbol: str = Query("BANKNIFTY")):
    """
    Placeholder option-chain snapshot API.
    Returns sample structure for both NIFTY and BANKNIFTY.
    Replace with real NSE fetcher later.
    """
    # Minimal sample payload
    sample = {
        "symbol": symbol.upper(),
        "spot": 59039 if symbol.upper().startswith("BANK") else 25910,
        "expiry": "THIS_WEEK",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        "strikes": [
            {"strike": 59000, "ce_ltp": 456.2, "pe_ltp": 120.5, "oi": 1200},
            {"strike": 59200, "ce_ltp": 351.75, "pe_ltp": 95.1, "oi": 900},
            {"strike": 59400, "ce_ltp": 264.9, "pe_ltp": 60.2, "oi": 400},
        ]
    }
    return {"status": "ok", "data": sample}
