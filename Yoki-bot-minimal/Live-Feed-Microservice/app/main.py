from fastapi import FastAPI
import redis
import json

app = FastAPI(title="Live Feed Microservice")

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


@app.get("/health")
def health():
    return {"status": "LIVE FEED RUNNING"}


@app.get("/tick/{instrument_key}")
def get_tick(instrument_key: str):
    data = r.get(instrument_key)

    if not data:
        return {
            "instrument_key": instrument_key,
            "ltp": None,
            "oi": 0
        }

    return json.loads(data)
