from fastapi import FastAPI
from app.upstox_ws import start_ws
from app.redis_client import redis_client
from contextlib import asynccontextmanager
from threading import Thread
from urllib.parse import unquote
import json
import time

# --- Runtime State ---
ws_status = {
    "running": False,
    "last_heartbeat": None
}

def ws_runner():
    """
    Wrapper around start_ws to track health status.
    If start_ws crashes, status will reflect failure.
    """
    try:
        ws_status["running"] = True
        ws_status["last_heartbeat"] = int(time.time())
        start_ws(heartbeat_callback=update_heartbeat)
    except Exception:
        ws_status["running"] = False


def update_heartbeat():
    ws_status["last_heartbeat"] = int(time.time())


@asynccontextmanager
async def lifespan(app: FastAPI):
    ws_thread = Thread(target=ws_runner, daemon=True)
    ws_thread.start()
    yield


app = FastAPI(title="Live Feed Microservice", lifespan=lifespan)


@app.get("/health")
def health():
    redis_ok = False
    try:
        redis_ok = redis_client.ping()
    except Exception:
        redis_ok = False

    heartbeat_age = None
    if ws_status["last_heartbeat"]:
        heartbeat_age = int(time.time()) - ws_status["last_heartbeat"]

    return {
        "websocket_running": ws_status["running"],
        "redis_connected": redis_ok,
        "last_heartbeat_seconds_ago": heartbeat_age
    }


@app.get("/tick/{instrument_key}")
def get_tick(instrument_key: str):
    decoded_key = unquote(instrument_key)

    try:
        raw = redis_client.get(decoded_key)
    except Exception as e:
        return {"error": "Redis connection failure", "detail": str(e)}

    if not raw:
        return {"error": "No live data yet"}

    try:
        payload = json.loads(raw)
    except Exception:
        return {"error": "Corrupted tick data"}

    # Optional freshness check (expects 'timestamp' in tick payload)
    if "timestamp" in payload:
        age = int(time.time()) - payload["timestamp"]
        if age > 5:
            return {"error": "Stale data", "age_seconds": age}

    return payload
