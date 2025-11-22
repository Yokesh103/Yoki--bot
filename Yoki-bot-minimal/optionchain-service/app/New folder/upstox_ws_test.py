import json
import websocket

ACCESS_TOKEN = "PASTE_YOUR_WORKIeyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI4QkFMRUgiLCJqdGkiOiI2OTIxOTU2MWNmYzJkNzQ4ZWQwN2MyZDgiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MzgwODYwOSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYzODQ4ODAwfQ.zB3B2fuCp13ji3BOxfKnIojo890FV6211LxEo6lG88kNG_ACCESS_TOKEN"

WS_URL = "wss://api.upstox.com/feed/market-data-feed"

def on_open(ws):
    print("✅ Connected to Upstox WebSocket")

    sub_msg = {
        "guid": "yoki-test-001",
        "method": "sub",
        "data": {
            "mode": "full",
            "instrument_keys": [
                "NSE_INDEX|Nifty 50"
            ]
        }
    }

    ws.send(json.dumps(sub_msg))


def on_message(ws, message):
    print("📈 Live Tick:", message)


def on_error(ws, error):
    print("❌ Error:", error)


def on_close(ws, close_status_code, close_msg):
    print("WebSocket Closed")


headers = [
    f"Authorization: Bearer {ACCESS_TOKEN}",
    "Accept: application/json"
]

ws = websocket.WebSocketApp(
    WS_URL,
    header=headers,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

ws.run_forever()
