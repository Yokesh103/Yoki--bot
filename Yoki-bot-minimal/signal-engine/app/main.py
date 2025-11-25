from fastapi import FastAPI
from app.db import init_db
from app.engine.evaluate_credit_spread import evaluate_credit_spread
from app.engine.models import DecideRequest
from app.engine.risk_guard import passes_risk_guard

app = FastAPI(title="Signal Engine")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/signal")
def generate_signal():

    dummy_request = DecideRequest(
        underlying="NIFTY",
        expiry="2025-07-31",        # ← MUST BE STRING
        spot=22450.0,
        instruments=[
            {
                "instrument_key": "NIFTY25JUL22300CE",
                "strike": 22300,
                "opt_type": "CE",
                "expiry": "2025-07-31",
                "oi": 10000,
                "ltp": 120
            },
            {
                "instrument_key": "NIFTY25JUL22100PE",
                "strike": 22100,
                "opt_type": "PE",
                "expiry": "2025-07-31",
                "oi": 8000,
                "ltp": 70
            }
        ],
        indicators={
            "adx14": 25.0,
            "rsi14": 55.0,
            "atr14": 120.5,
            "ivrank": 40.0,
            "vix": 13.2
        }
    )


    decision = evaluate_credit_spread(dummy_request)

    if decision.action == "NO_TRADE":
        return {"status": "rejected", "reason": decision.reason}

    ok, risk_reason = passes_risk_guard(decision.trade_payload["max_risk"])
    if not ok:
        return {"status": "rejected", "reason": risk_reason}

    return {
        "status": "ok",
        "signal": decision.model_dump(exclude_unset=True)
    }
