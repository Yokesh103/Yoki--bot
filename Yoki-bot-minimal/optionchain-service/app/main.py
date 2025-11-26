from fastapi import FastAPI, Query
from typing import Literal, List, Dict, Any
from datetime import date, datetime

from app.db import init_db, conn
from app.data_source import RestMarketDataSource
from app.option_chain_service import build_option_chain  # still used for manual endpoint


app = FastAPI(title="Option Chain Service")

init_db()
data_source = RestMarketDataSource()

# Mapping for index spot keys
INDEX_KEYS = {
    "NIFTY": "NSE_INDEX|Nifty 50",
    "BANKNIFTY": "NSE_INDEX|Nifty Bank",
}

# How many strikes above/below ATM to keep in /auto endpoint
STRIKE_WINDOW = 5


@app.get("/health")
def health():
    return {"status": "OK"}


@app.get("/expiries/{underlying}")
def list_expiries(underlying: str):
    """
    List ALL expiries available in the instruments DB for a given underlying.
    This is already returning real data from Upstox master.
    """
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT DISTINCT expiry FROM instruments WHERE underlying=? ORDER BY expiry",
        (underlying.upper(),)
    ).fetchall()
    return [r[0] for r in rows]


@app.get("/option-chain/{underlying}")
def get_option_chain(
    underlying: Literal["NIFTY", "BANKNIFTY"],
    expiry: str = Query(..., description="Expiry in YYYY-MM-DD"),
):
    """
    Manual expiry endpoint.
    You MUST pass a valid expiry from /expiries/{underlying}.
    """
    cur = conn.cursor()

    rows = cur.execute(
        """
        SELECT instrument_key, strike, opt_type, expiry, underlying
        FROM instruments
        WHERE underlying=? AND expiry=?
        """,
        (underlying, expiry),
    ).fetchall()

    if not rows:
        return {"error": "No instruments found for given underlying & expiry"}

    instruments: List[Dict[str, Any]] = [
        {
            "instrument_key": r[0],
            "strike": r[1],
            "opt_type": r[2],
            "expiry": r[3],
            "underlying": r[4],
        }
        for r in rows
    ]

    snapshot = data_source.get_snapshot(
        [inst["instrument_key"] for inst in instruments]
    )

    # Old behaviour: delegate to build_option_chain (simple structure)
    chain = build_option_chain(
        underlying=underlying,
        expiry=expiry,
        instruments=instruments,
        snapshot=snapshot,
    )
    return chain



    # 7) Determine strike range around ATM
    #    by index position in sorted strikes list
    atm_index = strikes.index(atm_strike)
    start = max(0, atm_index - strike_window)
    end = min(len(strikes) - 1, atm_index + strike_window)
    selected_strikes = set(strikes[start : end + 1])

    # 8) Build CE/PE tree for selected strikes
    tree: Dict[float, Dict[str, Dict[str, Any]]] = {}
    total_call_oi = 0
    total_put_oi = 0

    for inst in instruments:
        strike = inst["strike"]
        if strike not in selected_strikes:
            continue

        key = inst["instrument_key"]
        md = data.get(key, {}).get("market_data", {})

        ltp = md.get("last_traded_price")
        oi = md.get("oi", 0) or 0
        opt_type = inst["opt_type"]

        tree.setdefault(strike, {})
        tree[strike][opt_type] = {
            "instrument_key": key,
            "strike": strike,
            "opt_type": opt_type,
            "ltp": ltp,
            "oi": oi,
        }

    # 9) Aggregate rows + PCR
    strike_rows = []
    for strike in sorted(tree.keys()):
        ce = tree[strike].get("CE")
        pe = tree[strike].get("PE")

        if ce:
            total_call_oi += ce["oi"]
        if pe:
            total_put_oi += pe["oi"]

        strike_rows.append(
            {
                "strike": strike,
                "ce": ce,
                "pe": pe,
            }
        )

    pcr = round(total_put_oi / total_call_oi, 2) if total_call_oi else 0.0

    # 10) Strategy-ready response
    return {
        "underlying": underlying,
        "expiry": chosen_expiry,
        "spot": spot,
        "atm_strike": atm_strike,
        "pcr": pcr,
        "strike_window": strike_window,
        "strikes": strike_rows,
    }
