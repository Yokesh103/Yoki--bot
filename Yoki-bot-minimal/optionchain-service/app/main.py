from fastapi import FastAPI, Query
from typing import Literal
from app.db import init_db, conn
from app.data_source import RestMarketDataSource
from app.option_chain_service import build_option_chain

app = FastAPI(title="Option Chain Service")

init_db()
data_source = RestMarketDataSource()


@app.get("/health")
def health():
    return {"status": "OK"}


@app.get("/expiries/{underlying}")
def list_expiries(underlying: str):
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
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT instrument_key, strike, opt_type, expiry, underlying
        FROM instruments
        WHERE underlying=? AND expiry=?
    """, (underlying, expiry)).fetchall()

    if not rows:
        return {"error": "No instruments found for given underlying & expiry"}

    instruments = [
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

    chain = build_option_chain(
        underlying=underlying,
        expiry=expiry,
        instruments=instruments,
        snapshot=snapshot,
    )

    return chain
