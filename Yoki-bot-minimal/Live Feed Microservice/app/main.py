from fastapi import FastAPI
from app.cache import get_tick, get_all_ticks
from app.upstox_ws import run_ws_thread

app = FastAPI(title="Live Feed Service")

@app.on_event("startup")
def startup_event():
    run_ws_thread()


@app.get("/health")
def health():
    return {"status": "LIVE FEED RUNNING"}


@app.get("/live/{instrument_key}")
def get_live(instrument_key: str):
    tick = get_tick(instrument_key)
    if not tick:
        return {"error": "No live data for this instrument"}
    return tick


@app.get("/live-all")
def live_all():
    return get_all_ticks()
