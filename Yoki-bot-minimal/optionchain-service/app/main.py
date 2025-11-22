from fastapi import FastAPI, Query
from typing import Literal
from app.db import init_db
from app.data_source import RestMarketDataSource
from app.option_chain_service import build_option_chain

app = FastAPI(title="Option Chain Service")

init_db()
data_source = RestMarketDataSource()

@app.get("/option-chain/{underlying}")
def get_option_chain(
    underlying: Literal["NIFTY", "BANKNIFTY"],
    expiry: str = Query(..., description="Expiry in YYYY-MM-DD"),
):
    # TODO: load instrument list for this underlying+expiry from file or DB
    # For now, use mocked list or a small manually defined list

    instruments = []  # fill later
    snapshot = data_source.get_snapshot([inst["instrument_key"] for inst in instruments])

    chain = build_option_chain(
        underlying=underlying,
        expiry=expiry,
        instruments=instruments,
        snapshot=snapshot,
    )
    return chain
