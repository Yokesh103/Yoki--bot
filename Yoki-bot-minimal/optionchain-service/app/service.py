from typing import Dict, Any, List
from app.models import OptionChain, StrikeRow, OptionLeg

def build_option_chain(
    underlying: str,
    expiry: str,
    instruments: List[Dict[str, Any]],
    snapshot: Dict[str, Any],
) -> OptionChain:
    # instruments: list of {instrument_key, strike, opt_type, expiry, underlying}
    # snapshot: data returned from RestMarketDataSource.get_snapshot()

    # Upstox quote JSON shape: snapshot["data"][instrument_key]["market_data"]["last_traded_price"], etc.
    data = snapshot.get("data", {})

    tree: Dict[float, Dict[str, OptionLeg]] = {}

    for inst in instruments:
        key = inst["instrument_key"]
        info = data.get(key)
        if not info:
            continue

        md = info.get("market_data", {})
        ltp = md.get("last_traded_price")
        oi = md.get("oi", 0)

        strike = float(inst["strike"])
        opt_type = inst["opt_type"]  # "CE" / "PE"

        tree.setdefault(strike, {})
        tree[strike][opt_type] = OptionLeg(
            strike=strike,
            opt_type=opt_type,
            ltp=ltp,
            oi=oi,
        )

    rows: List[StrikeRow] = []
    total_call_oi = 0
    total_put_oi = 0

    for strike in sorted(tree.keys()):
        ce = tree[strike].get("CE")
        pe = tree[strike].get("PE")

        if ce:
            total_call_oi += ce.oi
        if pe:
            total_put_oi += pe.oi

        rows.append(StrikeRow(strike=strike, call=ce, put=pe))

    pcr = round(total_put_oi / total_call_oi, 2) if total_call_oi else 0.0

    return OptionChain(
        underlying=underlying,
        expiry=expiry,
        pcr=pcr,
        rows=rows,
    )
