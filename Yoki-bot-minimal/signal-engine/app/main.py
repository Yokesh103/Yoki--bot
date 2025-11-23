from fastapi import FastAPI
from app.engine.evaluate_credit_spread import evaluate_credit_spread
from app.engine.risk_guard import passes_risk_guard
from app.engine.decision_logger import log_decision
from app.db import init_db()
from app.alert_client import send_alert

app = FastAPI(title="Signal Engine")

init_db()

@app.get("/signal")
def generate_signal():
    data = {"spot": 22500, "adx": 18, "iv_rank": 40}

    # run strategy logic
    signal = evaluate_credit_spread(data)

    # risk validation
    if not passes_risk_guard(signal):
        log_decision("REJECTED", reason="Risk Check Failed", details=signal)
        return {"status": "rejected", "reason": "risk check failed"}

    # if everything is good → send alert
    send_alert(signal)
    log_decision("EXECUTED", details=signal)

    return {"status": "ok", "signal": signal}
