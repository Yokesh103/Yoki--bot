import json
import threading
from websocket import WebSocketApp
from app.cache import update_tick
from app.utils import extract_tick_data
from app.config import UPSTOX_ACCESS_TOKEN, UPSTOX_WS_URL


def on_message(ws, message):
    payload = json.loads(message)

    if "data" not in payload:
        return

    for tick in payload["data"]:
        inst_key = tick.get("instrument_key")
        if inst_key:
            clean = extract_tick_data(tick)
            update_tick(inst_key, clean)


def on_open(ws):
    # SUBSCRIBE TO LIVE INDEX + OPTIONS
    subscribe_payload = {
        "guid": "live-feed-001",
        "method": "sub",
        "data": {
            "mode": "full",
            "instrumentKeys": [
                "NSE_INDEX|Nifty 50",
                "NSE_INDEX|Nifty Bank"
            ]
        }
    }
    ws.send(json.dumps(subscribe_payload))


def start_ws():
    headers = [f"Authorization: Bearer {UPSTOX_ACCESS_TOKEN}"]

    ws = WebSocketApp(
        UPSTOX_WS_URL,
        header=headers,
        on_open=on_open,
        on_message=on_message
    )

    ws.run_forever()


def run_ws_thread():
    t = threading.Thread(target=start_ws, daemon=True)
    t.start()
