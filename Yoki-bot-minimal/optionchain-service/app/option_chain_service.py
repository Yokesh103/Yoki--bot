from typing import Dict, Any, List

def build_option_chain(underlying: str, expiry: str, instruments: List[Dict[str, Any]], snapshot: Dict[str, Any]):
    data = snapshot.get("data", {})

    rows = []

    for inst in instruments:
        key = inst["instrument_key"]
        md = data.get(key, {}).get("market_data", {})

        row = {
            "strike": inst["strike"],
            "type": inst["opt_type"],
            "ltp": md.get("last_traded_price"),
            "oi": md.get("oi", 0)
        }
        rows.append(row)

    return {
        "underlying": underlying,
        "expiry": expiry,
        "rows": rows
    }
