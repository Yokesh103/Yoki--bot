from app.config import *
from app.models import *
from typing import Dict, Any
from app.risk_guard import passes_risk_guard
from app.decision_logger import log_decision
from app.alert_client import send_alert
import math

def market_state(ind: IndicatorSnapshot) -> str:
    if ind.adx14 > ADX_TREND:
        return "TREND"
    if ind.adx14 >= ADX_RANGE_LOW:
        return "RANGE"
    return "FLAT"

def compute_premium_after_charges(gross_premium: float) -> float:
    return gross_premium - SIMULATED_CHARGES

def choose_strikes_for_credit(instruments: list, spot: float) -> Dict[str, Any]:
    # simple: find OTM short ~ spot +/- 150..200, prefer strikes with high OI - placeholder
    # instruments is list of dicts with strike,opt_type
    # return short, hedge strike and premiums simulated (must be fetched via optionchain service)
    short = None
    hedge = None
    # simple stub: pick nearest strikes
    strikes = sorted({i["strike"] for i in instruments})
    # choose short as strike nearest to spot + 180 or -180 depending on RSI later; simplified here
    nearest = min(strikes, key=lambda s: abs(s - spot - 180))
    short = nearest
    hedge = short - 200  # for puts example
    return {"short": short, "hedge": hedge}

def evaluate_credit_spread(req: DecideRequest) -> DecisionResult:
    # This should query instrument premiums from option-chain snapshot (passed into req.instruments)
    # For prototype we assume instruments include premium fields or use external call. Placeholder:
    strikes = choose_strikes_for_credit([i.dict() for i in req.instruments], req.spot)
    gross_premium = 300.0  # placeholder. Replace with real quote lookup
    net_premium = compute_premium_after_charges(gross_premium)
    max_risk = 2000.0  # placeholder calc (width * lotsize - net_premium)
    passes, reason = passes_risk_guard(max_risk)
    decision = {
        "action": "TRADE" if passes and net_premium >= PREMIUM_THRESHOLD else "NO_TRADE",
        "strategy": "CREDIT_SPREAD",
        "reason": None if passes and net_premium >= PREMIUM_THRESHOLD else ("RISK_FAIL" if not passes else "PREMIUM_TOO_LOW"),
        "trade_payload": {
            "short_strike": strikes["short"],
            "hedge_strike": strikes["hedge"],
            "gross_premium": gross_premium,
            "net_premium": net_premium,
            "max_risk": max_risk
        }
    }
    # log
    dec_id = log_decision({
        "underlying": req.underlying,
        "expiry": req.expiry,
        "market_state": market_state(req.indicators),
        "filter_data": req.indicators.dict(),
        "strategy_selected": "CREDIT_SPREAD",
        "rejection_reason": decision["reason"],
        "strikes_chosen": decision["trade_payload"],
        "confidence_score": 80,
        "execution_status": "PAPER_RECOMMEND" if decision["action"] == "TRADE" else "PAPER_REJECT",
        "premium_after_charges": net_premium,
        "max_risk": max_risk,
        "raw_payload": req.dict()
    })
    decision["decision_id"] = dec_id
    # alert
    send_alert({
        "type": "TRADE_SIGNAL" if decision["action"] == "TRADE" else "TRADE_REJECT",
        "id": dec_id,
        "strategy": "CREDIT_SPREAD",
        **decision["trade_payload"]
    })
    return DecisionResult(**decision)
