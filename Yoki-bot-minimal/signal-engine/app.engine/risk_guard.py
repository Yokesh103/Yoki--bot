from app.config import WORKING_CAPITAL, MAX_RISK_PER_TRADE, MONTHLY_LOSS_LIMIT

def passes_risk_guard(max_risk: float) -> (bool, str):
    if max_risk > MAX_RISK_PER_TRADE:
        return False, f"MAX_RISK_EXCEEDED_{max_risk}"
    # Monthly loss check should query historical PnL from DB - simplified here
    # Implement PnL aggregation to enforce MONTHLY_LOSS_LIMIT in production.
    return True, "OK"
