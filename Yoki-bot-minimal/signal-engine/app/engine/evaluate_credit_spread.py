# app/engine/evaluate_credit_spread.py
from app.engine.models import DecideRequest, DecisionResult
from app.config import SIMULATED_CHARGES, PREMIUM_THRESHOLD
from uuid import uuid4
import logging

LOGGER = logging.getLogger("signal_engine")
# tune these or move to config
MIN_DISTANCE = 150
MAX_DISTANCE = 200
HEDGE_GAP = 200

def evaluate_credit_spread(req: DecideRequest) -> DecisionResult:
    dec_id = str(uuid4())
    insts = [i.dict() for i in req.instruments]

    # consider only the intended side — keep this strict for now
    pes = [i for i in insts if i.get("opt_type") == "PE"]

    # debugging info
    LOGGER.debug("spot=%s, available_pe_strikes=%s", req.spot, [i["strike"] for i in pes])

    candidates = []
    for i in pes:
        diff = req.spot - i["strike"]
        if MIN_DISTANCE <= diff <= MAX_DISTANCE:
            candidates.append((i, diff))

    if not candidates:
        # return richer diagnostic info to help debugging
        return DecisionResult(
            action="NO_TRADE",
            strategy="CREDIT_SPREAD",
            reason="NO_STRIKE_IN_RANGE",
            trade_payload={
                "spot": req.spot,
                "available_pe_strikes": [i["strike"] for i in pes],
                "required_distance": [MIN_DISTANCE, MAX_DISTANCE]
            },
            decision_id=dec_id
        )

    # choose short leg by highest OI (as before)
    short_leg = max((c[0] for c in candidates), key=lambda x: x.get("oi", 0))

    hedge_candidates = [i for i in pes if i["strike"] == short_leg["strike"] - HEDGE_GAP]

    if not hedge_candidates:
        return DecisionResult(
            action="NO_TRADE",
            strategy="CREDIT_SPREAD",
            reason="NO_HEDGE_STRIKE",
            trade_payload={
                "short_strike": short_leg["strike"],
                "required_hedge": short_leg["strike"] - HEDGE_GAP,
                "available_pe_strikes": [i["strike"] for i in pes]
            },
            decision_id=dec_id
        )

    hedge_leg = hedge_candidates[0]
    short_prem = short_leg["ltp"]
    hedge_prem = hedge_leg["ltp"]
    gross_premium = short_prem - hedge_prem
    net_premium = gross_premium - SIMULATED_CHARGES
    max_risk = (short_leg["strike"] - hedge_leg["strike"]) * 50 - gross_premium * 50

    if net_premium < PREMIUM_THRESHOLD:
        return DecisionResult(
            action="NO_TRADE",
            strategy="CREDIT_SPREAD",
            reason="PREMIUM_TOO_LOW",
            trade_payload={
                "gross_premium": gross_premium,
                "net_premium": net_premium,
                "premium_threshold": PREMIUM_THRESHOLD
            },
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
