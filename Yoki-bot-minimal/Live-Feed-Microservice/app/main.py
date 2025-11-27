from fastapi import FastAPI
from app.upstox_ws import start_ws
from app.redis_client import redis_client
import json

app = FastAPI(title="Live Feed Microservice")


@app.on_event("startup")
def boot():
    start_ws()


@app.get("/health")
def health():
    return {"status": "LIVE FEED RUNNING"}


@app.get("/tick/{instrument_key}")
def get_tick(instrument_key: str):
    data = redis_client.get(instrument_key)

    if not data:
        return {"error": "No live data yet"}

    return json.loads(data)
