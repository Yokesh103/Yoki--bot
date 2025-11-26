from fastapi import FastAPI
from typing import Literal
from app.db import init_db
from app.data_source import RestMarketDataSource
from app.option_chain_service import build_option_chain
from app.db_instruments import get_instruments_from_db

app = FastAPI(title="Option Chain Service")

init_db()
data_source = RestMarketDataSource()


@app.get("/health")
def health():
    return {"status": "OK"}


# ================= STANDARD ENDPOINT =================
@app.get("/option-chain/{underlying}")
def get_option_chain(
    underlying: Literal["NIFTY", "BANKNIFTY"],
    expiry: str
):
    instruments = get_instruments_from_db(underlying, expiry)

    if not instruments:
        return {"error": "No instruments found for given underlying & expiry"}

    snapshot = data_source.get_snapshot(
        [inst["instrument_key"] for inst in instruments]
    )

    chain = build_option_chain(
        underlying=underlying,
        expiry=expiry,
        instruments=instruments,
        snapshot=snapshot,
    )

    return chain


# ✅ ✅ ✅ AUTO STRATEGY ENDPOINT ✅ ✅ ✅
@app.get("/option-chain/{underlying}/auto")
def get_option_chain_auto(underlying: Literal["NIFTY", "BANKNIFTY"]):

    instruments = get_instruments_from_db(underlying)

    if not instruments:
        return {"error": "No instruments loaded for underlying"}

    all_strikes = sorted({inst["strike"] for inst in instruments})
    if not all_strikes:
        return {"error": "No strikes available to derive spot"}

    # Approximate spot by median strike
    mid = len(all_strikes) // 2
    spot = float(all_strikes[mid])

    # Detect ATM
    atm_strike = min(all_strikes, key=lambda x: abs(x - spot))

    # Filter ± 500 point strikes
    filtered = [
        i for i in instruments
        if abs(i["strike"] - atm_strike) <= 500
    ]

    if not filtered:
        return {"error": "No strikes in ATM range"}

    snapshot = data_source.get_snapshot(
        [inst["instrument_key"] for inst in filtered]
    )

    chain = build_option_chain(
        underlying=underlying,
        expiry=filtered[0]["expiry"],
        instruments=filtered,
        snapshot=snapshot,
    )

    return {
        "underlying": underlying,
        "spot": spot,
        "atm": atm_strike,
        "expiry": filtered[0]["expiry"],
        "data": chain
    }
