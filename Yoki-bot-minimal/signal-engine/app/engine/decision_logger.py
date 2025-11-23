import json, uuid, datetime
from app.db import get_conn

def log_decision(payload: dict) -> str:
    conn = get_conn()
    cur = conn.cursor()
    id_ = str(uuid.uuid4())
    cur.execute("""
    INSERT INTO trade_decision_logs (
        id, timestamp, underlying, expiry, market_state,
        filter_data, strategy_selected, rejection_reason, strikes_chosen,
        confidence_score, execution_status, premium_after_charges, max_risk, pnl_after_charges, raw_payload
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        id_,
        datetime.datetime.utcnow().isoformat(),
        payload.get("underlying"),
        payload.get("expiry"),
        payload.get("market_state"),
        json.dumps(payload.get("filter_data", {})),
        payload.get("strategy_selected"),
        payload.get("rejection_reason"),
        json.dumps(payload.get("strikes_chosen", {})),
        payload.get("confidence_score"),
        payload.get("execution_status"),
        payload.get("premium_after_charges"),
        payload.get("max_risk"),
        payload.get("pnl_after_charges"),
        json.dumps(payload)
    ))
    conn.commit()
    return id_
