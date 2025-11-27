import json
import websocket
from app.redis_client import redis_client
from app.config import UPSTOX_ACCESS_TOKEN

WS_URL = "wss://api.upstox.com/v2/feed/market-data-feed"


def on_message(ws, message):
    data = json.loads(message)
    feeds = data.get("feeds", {})

    for instrument_key, content in feeds.items():
        market = content.get("ff", {}).get("marketFF", {})

        payload = {
            "ltp": market.get("ltp"),
            "oi": market.get("oi", 0)
        }

        redis_client.set(instrument_key, json.dumps(payload))
        print(f"📡 TICK RECEIVED -> {instrument_key} | LTP: {payload['ltp']} | OI: {payload['oi']}")


def on_open(ws):
    print("✅ Upstox WebSocket Connected & Subscribed")

    ws.send(json.dumps({
        "guid": "live-feed",
        "method": "sub",
        "data": {
            "mode": "full",
            "instrumentKeys": [
                "NSE_INDEX|Nifty 50",
                "NSE_FO|46879"
            ]
        }
    }))


def start_ws():
    ws = websocket.WebSocketApp(
        WS_URL,
        header=[f"Authorization: Bearer {UPSTOX_ACCESS_TOKEN}"],
        on_message=on_message,
        on_open=on_open
    )
    ws.run_forever()
