from fastapi import FastAPI, Query
from typing import Literal
from app.db import init_db
from app.data_source import RestMarketDataSource
from app.option_chain_service import build_option_chain

app = FastAPI(title="Option Chain Service")

init_db()
data_source = RestMarketDataSource()

# TEMP MOCK INSTRUMENTS (just to prove pipeline works)
MOCK_INSTRUMENTS = [
    {
        "instrument_key": "NSE_FO|123456",
        "strike": 22000,
        "opt_type": "CE",
        "expiry": "2025-11-27",
        "underlying": "NIFTY",
    },
    {
        "instrument_key": "NSE_FO|123457",
        "strike": 22000,
        "opt_type": "PE",
        "expiry": "2025-11-27",
        "underlying": "NIFTY",
    }
]

@app.get("/health")
def health():
    return {"status": "OK"}

@app.get("/option-chain/{underlying}")
def get_option_chain(
    underlying: Literal["NIFTY", "BANKNIFTY"],
    expiry: str = Query(..., description="Expiry in YYYY-MM-DD"),
):
    instruments = [
        i for i in MOCK_INSTRUMENTS 
        if i["underlying"] == underlying and i["expiry"] == expiry
    ]

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
