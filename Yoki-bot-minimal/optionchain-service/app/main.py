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


@app.get("/option-chain/{underlying}/auto")
def get_option_chain_auto(
    underlying: Literal["NIFTY", "BANKNIFTY"],
    strike_window: int = Query(STRIKE_WINDOW, ge=1, le=30),
):
    """
    Strategy-ready endpoint.

    - Chooses nearest valid expiry >= today
    - Fetches spot from index quote
    - Determines ATM strike
    - Returns only strikes around ATM (± strike_window)
    - Computes PCR from filtered strikes
    """

    underlying = underlying.upper()
    cur = conn.cursor()

    # 1) Get all expiries for underlying
    exp_rows = cur.execute(
        "SELECT DISTINCT expiry FROM instruments WHERE underlying=? ORDER BY expiry",
        (underlying,),
    ).fetchall()
    if not exp_rows:
        return {"error": f"No expiries found for {underlying}"}

    expiries = [r[0] for r in exp_rows]

    # 2) Pick nearest expiry >= today, else earliest
    today = date.today()
    def parse_exp(e: str) -> date:
        return datetime.strptime(e, "%Y-%m-%d").date()

    future_exps = [e for e in expiries if parse_exp(e) >= today]
    chosen_expiry = future_exps[0] if future_exps else expiries[0]

    # 3) Load all instruments for that expiry
    rows = cur.execute(
        """
        SELECT instrument_key, strike, opt_type, expiry, underlying
        FROM instruments
        WHERE underlying=? AND expiry=?
        """,
        (underlying, chosen_expiry),
    ).fetchall()

    if not rows:
        return {"error": f"No instruments found for {underlying} @ {chosen_expiry}"}

    instruments: List[Dict[str, Any]] = [
        {
            "instrument_key": r[0],
            "strike": float(r[1]),
            "opt_type": r[2],
            "expiry": r[3],
            "underlying": r[4],
        }
        for r in rows
    ]

    # 4) Get snapshot INCLUDING index spot
    index_key = INDEX_KEYS.get(underlying)
    if not index_key:
        return {"error": f"No index mapping for underlying {underlying}"}

    all_keys = [inst["instrument_key"] for inst in instruments] + [index_key]
    snapshot = data_source.get_snapshot(all_keys)
    data = snapshot.get("data", {})

    # 5) Extract spot
    index_md = data.get(index_key, {}).get("market_data", {})
    spot = index_md.get("last_traded_price")
    if not spot:
        return {"error": "Unable to fetch spot from index quote"}

    # 6) Determine ATM strike (closest strike to spot)
    strikes = sorted({inst["strike"] for inst in instruments})
    atm_strike = min(strikes, key=lambda s: abs(s - spot))

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
