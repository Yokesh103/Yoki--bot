import json
import websocket
from google.protobuf.json_format import MessageToDict
from MarketDataFeed_pb2 import FeedResponse

ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI4QkFMRUgiLCJqdGkiOiI2OTI4YTNlZWJhYWE3ODQyOWRmMzBiMjQiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2NDI3MTA4NiwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzY0MjgwODAwfQ.X8H0MXmmsEBogc19PuGxsnHwUtf4uvzwxtW5P8sOTb4"
WS_URL = "wss://api.upstox.com/v3/feed/market-data-feed"


def on_message(ws, message):
    feed = FeedResponse()
    feed.ParseFromString(message)
    data = MessageToDict(feed)

    print("\n📈 LIVE MARKET DATA:")
    print(json.dumps(data, indent=2))


def on_open(ws):
    print("✅ Connected to Upstox V3")

    payload = {
        "guid": "v3-test",
        "method": "sub",
        "data": {
            "mode": "ltpc",
            "instrumentKeys": ["NSE_EQ|RELIANCE"]
        }
    }

    ws.send(json.dumps(payload))
    print("📨 Subscription sent")


headers = [
    f"Authorization: Bearer {ACCESS_TOKEN}"
]

ws = websocket.WebSocketApp(
    WS_URL,
    header=headers,
    on_open=on_open,
    on_message=on_message
)

ws.run_forever()
