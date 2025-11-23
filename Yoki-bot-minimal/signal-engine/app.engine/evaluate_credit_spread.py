def evaluate_credit_spread(req: DecideRequest) -> DecisionResult:
    insts = [i.dict() for i in req.instruments]

    # 1. Filter only PE side for down-side credit spread example
    pes = [i for i in insts if i["opt_type"] == "PE"]

    # 2. Pick short strike ~150–200 points below spot, highest OI
    candidates = [
        i for i in pes
        if 150 <= (req.spot - i["strike"]) <= 200
    ]
    if not candidates:
        return DecisionResult(action="NO_TRADE", strategy="CREDIT_SPREAD",
                              reason="NO_STRIKE_IN_RANGE", trade_payload=None)

    short_leg = max(candidates, key=lambda x: x.get("oi", 0))  # OI wall
    # 3. Hedge 200 points lower
    hedge_candidates = [i for i in pes if i["strike"] == short_leg["strike"] - 200]
    if not hedge_candidates:
        return DecisionResult(action="NO_TRADE", strategy="CREDIT_SPREAD",
                              reason="NO_HEDGE_STRIKE", trade_payload=None)

    hedge_leg = hedge_candidates[0]

    short_prem = short_leg["ltp"]
    hedge_prem = hedge_leg["ltp"]
    gross_premium = short_prem - hedge_prem

    net_premium = gross_premium - SIMULATED_CHARGES
    max_risk = (short_leg["strike"] - hedge_leg["strike"]) * 50 - gross_premium * 50  # 50 lot size

    ok, risk_reason = passes_risk_guard(max_risk)

    if not ok:
        reason = risk_reason
        action = "NO_TRADE"
    elif net_premium < PREMIUM_THRESHOLD:
        reason = "PREMIUM_TOO_LOW"
        action = "NO_TRADE"
    else:
        reason = None
        action = "TRADE"

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

    # log + alert (reuse your existing logger/alert code)
    # ...

    return DecisionResult(
        action=action,
        strategy="CREDIT_SPREAD",
        reason=reason,
        trade_payload=trade_payload,
        decision_id=dec_id,
    )
