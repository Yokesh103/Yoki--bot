# greeks-service/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="greeks-service")

class GreeksRequest(BaseModel):
    ltp: float
    strike: float
    ttm_days: Optional[float] = 7
    option_type: Optional[str] = "CE"  # CE or PE
    underlying: Optional[float] = None

@app.get("/")
async def root():
    return {"detail": "greeks-service alive. POST /compute for greeks."}

@app.post("/compute")
async def compute(req: GreeksRequest):
    # This is a simple stub. Replace with Black-76 or py_vollib as next step.
    # Return plausible dummy greeks scaled with moneyness
    moneyness = (req.underlying or req.strike) / max(1.0, req.strike)
    delta = 0.5 if req.option_type == "CE" else -0.5
    gamma = 0.01
    theta = -0.02 * (req.ttm_days / 7.0)
    vega = 0.1
    return {
        "ltp": req.ltp,
        "strike": req.strike,
        "option_type": req.option_type,
        "delta": round(delta, 4),
        "gamma": round(gamma, 5),
        "theta": round(theta, 5),
        "vega": round(vega, 5),
        "note": "stub greeks; replace with py_vollib/Black76 for production"
    }
