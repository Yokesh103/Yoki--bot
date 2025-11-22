# signal-engine/main.py
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI(title="signal-engine")

@app.get("/signal")
async def signal(strategy: str = Query("butterfly"), symbol: str = Query("BANKNIFTY")):
    """
    Unified signal endpoint.
    strategy: butterfly | debitspread
    symbol: BANKNIFTY | NIFTY
    """
    s = strategy.lower()
    sym = symbol.upper()
    # Minimal heuristic to return strikes and suggested action
    if s == "butterfly":
        # ATM nearest 100 rounding (example)
        spot = 59039 if sym.startswith("BANK") else 25910
        atm = round(spot/100)*100
        # use +200 and +400 for OTM buys/sells
        sell = atm + 200
        buy_far = atm + 400
        return {
            "strategy": "butterfly",
            "symbol": sym,
            "atm": int(atm),
            "sell": int(sell),
            "buy_far": int(buy_far),
            "net_debit_estimate": 150,
            "timing": "10:45-12:00 preferred",
            "status": "watch"
        }
    elif s == "debitspread":
        spot = 25910 if sym == "NIFTY" else 59039
        atm = round(spot/50)*50
        sell = atm + 50
        return {
            "strategy": "debitspread",
            "symbol": sym,
            "buy_atm": int(atm),
            "sell_otm": int(sell),
            "net_debit_estimate": 40,
            "timing": "10:15-12:30",
            "status": "watch"
        }
    else:
        return {"status":"error", "message":"unknown strategy"}
