import json
import redis
import websocket
from app.config import UPSTOX_ACCESS_TOKEN

REDIS_HOST = "localhost"
REDIS_PORT = 6379

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

WS_URL = "wss://api.upstox.com/v2/feed/market-data-feed"


def on_message(ws, message):
    data = json.loads(message)

    feeds = data.get("feeds", {})
    for instrument_key, content in feeds.items():
        market = content.get("ff", {}).get("marketFF", {})

        ltp = market.get("ltp")
        oi = market.get("oi", 0)

        payload = {
            "instrument_key": instrument_key,
            "ltp": ltp,
            "oi": oi
        }

        r.set(instrument_key, json.dumps(payload))


def on_open(ws):
    print("✅ Upstox WebSocket Connected")

    subscribe_payload = {
        "guid": "live-feed",
        "method": "sub",
        "data": {
            "mode": "full",
            "instrumentKeys": [
                "NSE_INDEX|Nifty 50"
            ]
        }
    }

    ws.send(json.dumps(subscribe_payload))


def start_ws():
    headers = {
        "Authorization": f"Bearer {UPSTOX_ACCESS_TOKEN}"
    }

    ws = websocket.WebSocketApp(
        WS_URL,
        header=[f"{k}: {v}" for k, v in headers.items()],
        on_message=on_message,
