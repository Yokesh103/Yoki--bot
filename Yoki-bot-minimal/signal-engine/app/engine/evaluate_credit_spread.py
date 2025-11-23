# signal-engine/app/engine/evaluate_credit_spread.py

from app.engine.models import DecideRequest, DecisionResult
# NOTE: remove passes_risk_guard import from here — risk check happens in API layer
from app.config import SIMULATED_CHARGES, PREMIUM_THRESHOLD
from uuid import uuid4


def evaluate_credit_spread(req: DecideRequest) -> DecisionResult:
    dec_id = str(uuid4())

    # If you're on Pydantic v2, consider using model_dump(); keep .dict() if it works for you.
    insts = [i.dict() for i in req.instruments]

    pes = [i for i in insts if i["opt_type"] == "PE"]

    candidates = [
        i for i in pes
        if 150 <= (req.spot - i["strike"]) <= 200
    ]

    if not candidates:
        return DecisionResult(
            action="NO_TRADE",
            strategy="CREDIT_SPREAD",
            reason="NO_STRIKE_IN_RANGE",
            trade_payload=None,
            decision_id=dec_id
        )

    short_leg = max(candidates, key=lambda x: x.get("oi", 0))

    hedge_candidates = [
        i for i in pes
        if i["strike"] == short_leg["strike"] - 200
    ]

    if not hedge_candidates:
        return DecisionResult(
            action="NO_TRADE",
            strategy="CREDIT_SPREAD",
            reason="NO_HEDGE_STRIKE",
            trade_payload=None,
            decision_id=dec_id
        )

    hedge_leg = hedge_candidates[0]

    short_prem = short_leg["ltp"]
    hedge_prem = hedge_leg["ltp"]
    gross_premium = short_prem - hedge_prem

    net_premium = gross_premium - SIMULATED_CHARGES

    # calculate max risk but do NOT enforce it here
    max_risk = (short_leg["strike"] - hedge_leg["strike"]) * 50 - gross_premium * 50

    # Decision logic: premium threshold only (keep strategy-level rejection)
    if net_premium < PREMIUM_THRESHOLD:
        return DecisionResult(
            action="NO_TRADE",
            strategy="CREDIT_SPREAD",
            reason="PREMIUM_TOO_LOW",
            trade_payload=None,
            decision_id=dec_id
        )

    trade_payload = {
        "underlying": req.underlying,
        "expiry": req.expiry,
        "type": "PE_CREDIT_SPREAD",
        "short_strike": short_leg["strike"],
        "hedge_strike": hedge_leg["strike"],
        "short_premium": short_prem,
        "hedge_premium": hedge_prem,
        "gross_premium": gross_premium,
        "net_premium": net_premium,
        "max_risk": max_risk,
    }

    return DecisionResult(
        action="TRADE",
        strategy="CREDIT_SPREAD",
        reason=None,
        trade_payload=trade_payload,
        decision_id=dec_id
    )
