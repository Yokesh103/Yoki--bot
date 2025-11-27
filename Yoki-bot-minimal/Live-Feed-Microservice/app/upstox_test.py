import websocket
import json

TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI4QkFMRUgiLCJqdGkiOiI2OTI4OTQ1ODczYjRiNDI3OWFlNTJmMzciLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2NDI2NzA5NiwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzY0MjgwODAwfQ.wWpUfvHmVlFUfRkeGes4D1lDyIifOgUYAgl9PzNHdtc"

def on_message(ws, msg):
    print("MESSAGE:", msg)

def on_open(ws):
    print("CONNECTED")
    ws.send(json.dumps({
        "guid": "test",
        "method": "sub",
        "data": {
            "mode": "full",
            "instrumentKeys": ["NSE_EQ|RELIANCE"]
        }
    }))

ws = websocket.WebSocketApp(
    "wss://api.upstox.com/v2/feed/market-data-feed",
    header=[f"Authorization: Bearer {TOKEN}"],
    on_message=on_message,
    on_open=on_open
)

ws.run_forever()
