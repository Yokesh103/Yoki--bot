# app.py
import os
import json
import time
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from threading import Thread
from urllib.parse import unquote

from redis_client import redis_client
from streamer import create_and_start_streamer

# runtime state
ws_status = {"running": False, "last_heartbeat": None}
streamer_instance = None

def update_heartbeat():
    ws_status["last_heartbeat"] = int(time.time())

@asynccontextmanager
async def lifespan(app: FastAPI):
    global streamer_instance
    # start streamer in background thread
    def runner():
        global streamer_instance
        try:
            streamer_instance = create_and_start_streamer()
            ws_status["running"] = True
            ws_status["last_heartbeat"] = int(time.time())
        except Exception as e:
            print("streamer start failed:", e)
            ws_status["running"] = False

    thread = Thread(target=runner, daemon=True)
    thread.start()
    yield
    # on shutdown
    try:
        if streamer_instance:
            streamer_instance.stop()
    except Exception:
        pass

app = FastAPI(title="AngelOne Live Feed Microservice", lifespan=lifespan)

REDIS_PREFIX = os.getenv("REDIS_PREFIX", "angel:tick:")

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

    return {"websocket_running": ws_status["running"], "redis_connected": redis_ok, "last_heartbeat_seconds_ago": heartbeat_age}

@app.get("/tick/{token}")
def get_tick(token: str):
    tok = unquote(token)
    key = REDIS_PREFIX + tok
    try:
        raw = redis_client.get(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection failure: {e}")

    if not raw:
        raise HTTPException(status_code=404, detail="No live data yet for token")

    try:
        payload = json.loads(raw)
    except Exception:
        raise HTTPException(status_code=500, detail="Malformed tick data")

    # freshness check: payload['timestamp'] in ms
    if "timestamp" in payload:
        age_seconds = (int(time.time() * 1000) - payload["timestamp"]) / 1000.0
        payload["age_seconds"] = round(age_seconds, 3)

    return payload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8300")), reload=False)
