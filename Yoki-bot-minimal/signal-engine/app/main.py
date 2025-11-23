from fastapi import FastAPI
from app.db import init_db
from app.engine.evaluate_credit_spread import evaluate_credit_spread
from app.engine.models import DecideRequest, Instrument
from app.engine.risk_guard import passes_risk_guard

app = FastAPI(title="Signal Engine")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/signal")
def generate_signal():

    # MOCK DATA (will later come from option-chain service)
    request = DecideRequest(
        underlying="NIFTY",
        expiry="2025-11-27",
        spot=22500,
        instruments=[
            Instrument(strike=22300, opt_type="PE", ltp=120, oi=150000),
            Instrument(strike=22100, opt_type="PE", ltp=60, oi=90000),
        ]
    )

    decision = evaluate_credit_spread(request)

    if decision.action == "NO_TRADE":
        return {
            "status": "rejected",
            "reason": decision.reason
        }

    ok, risk_reason = passes_risk_guard(decision.trade_payload["max_risk"])

    if not ok:
        return {
            "status": "rejected",
            "reason": risk_reason
        }

    return {
        "status": "ok",
        "signal": decision.model_dump(exclude_unset=True)
    }
