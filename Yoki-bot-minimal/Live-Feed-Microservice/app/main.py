from fastapi import FastAPI
from app.upstox_ws import start_ws
from app.redis_client import redis_client
import json
from threading import Thread
from urllib.parse import unquote

app = FastAPI(title="Live Feed Microservice")

@app.on_event("startup")
def boot():
    Thread(target=start_ws, daemon=True).start()

@app.get("/health")
def health():
    return {"status": "LIVE FEED RUNNING"}

@app.get("/tick/{instrument_key}")
def get_tick(instrument_key: str):
    decoded_key = unquote(instrument_key)
    data = redis_client.get(decoded_key)

    if not data:
        return {"error": "No live data yet"}

    return json.loads(data)
