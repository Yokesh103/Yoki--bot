from fastapi import FastAPI
from app.models import DecideRequest, DecisionResult
from app.engine import market_state, evaluate_credit_spread
from app.config import OPTIONCHAIN_SERVICE_URL
import requests

app = FastAPI(title="Signal Engine")

@app.post("/decide", response_model=DecisionResult)
def decide(req: DecideRequest):
    # master controller
    ms = market_state(req.indicators)
    # hard exclusions
    if req.indicators.vix and req.indicators.vix > 25:
        # log rejection and return
        return DecisionResult(action="NO_TRADE", strategy=None, reason="VIX_PANIC", trade_payload=None)
    # ADX-first gating and selection
    if ms == "TREND":
        # call directional evaluator (not implemented here)
        return DecisionResult(action="NO_TRADE", strategy="DIRECTIONAL", reason="NOT_IMPLEMENTED", trade_payload=None)
    # expiry/time -> butterfly decision is done inside other evaluators
    # condor check if ivrank high... delegating to credit spread for now
    return evaluate_credit_spread(req)
