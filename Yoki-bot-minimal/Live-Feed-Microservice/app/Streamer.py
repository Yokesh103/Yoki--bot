# streamer.py
import os
import json
import time
import threading
from typing import List
import websocket
from dotenv import load_dotenv

from decoder import decode_ltp_packet
from redis_client import redis_client

load_dotenv()

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
FEED_TOKEN = os.getenv("ANGEL_FEED_TOKEN")
WS_BASE = os.getenv("ANGEL_WS_BASE", "wss://smartapisocket.angelone.in/smart-stream")
REDIS_PREFIX = os.getenv("REDIS_PREFIX", "angel:tick:")

TOKENS_CSV = os.getenv("SUBSCRIBE_TOKENS", "")
TOKENS = [t.strip() for t in TOKENS_CSV.split(",") if t.strip()]

if not (API_KEY and CLIENT_CODE and FEED_TOKEN):
    raise SystemExit("ANGEL_API_KEY, ANGEL_CLIENT_CODE and ANGEL_FEED_TOKEN environment variables must be set")

def build_ws_url():
    return f"{WS_BASE}?clientCode={CLIENT_CODE}&feedToken={FEED_TOKEN}&apiKey={API_KEY}"

class AngelStreamer:
    def __init__(self, tokens: List[str]):
        self.ws_url = build_ws_url()
        self.tokens = tokens
        self.ws = None
        self._stop = threading.Event()

    def start(self):
        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        t = threading.Thread(target=self._run_forever, daemon=True)
        t.start()

        hb = threading.Thread(target=self._heartbeat_ping, daemon=True)
        hb.start()

    def _run_forever(self):
        while not self._stop.is_set():
            try:
                print("Connecting to", self.ws_url)
                # websocket-client will block until closed
                self.ws.run_forever()
            except Exception as e:
                print("WS run error:", e)
            time.sleep(3)

    def stop(self):
        self._stop.set()
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass

    def _heartbeat_ping(self):
        while not self._stop.is_set():
            try:
                # SmartStream expects textual 'ping'
                if self.ws and getattr(self.ws, "sock", None) and self.ws.sock and getattr(self.ws.sock, "connected", False):
                    self.ws.send("ping")
            except Exception as e:
                print("heartbeat send error:", e)
            time.sleep(30)

    def on_open(self, ws):
        print("WS connected")
        if self.tokens:
            self.subscribe(self.tokens, mode=1)

    def on_close(self, ws, code, reason):
        print("WS closed", code, reason)

    def on_error(self, ws, err):
        print("WS error", err)

    def on_message(self, ws, message):
        # binary LTP packets expected
        if isinstance(message, bytes):
            decoded = decode_ltp_packet(message)
            if "error" not in decoded:
                key = REDIS_PREFIX + decoded["token"]
                payload = {
                    "mode": decoded["mode"],
                    "exchange_type": decoded["exchange_type"],
                    "token": decoded["token"],
                    "sequence_no": decoded["sequence_no"],
                    "timestamp": decoded["timestamp"],
                    "ltp": decoded["ltp"],
                    "received_ts": int(time.time() * 1000)
                }
                try:
                    redis_client.set(key, json.dumps(payload))
                except Exception as e:
                    print("Redis set error:", e)
                print("DECODED:", payload)
            else:
                print("Decode error:", decoded)
        else:
            # text messages: pong, subscription ack, or errors
            txt = str(message)
            print("TEXT MSG:", txt[:500])

    def subscribe(self, tokens: List[str], mode: int = 1):
        token_groups = [{"exchangeType": 1, "tokens": tokens}]
        req = {
            "correlationID": "sub-" + str(int(time.time())),
            "action": 1,
            "params": {
                "mode": mode,
                "tokenList": token_groups
            }
        }
        try:
            self.ws.send(json.dumps(req))
            print("Subscribe request sent:", req["correlationID"])
        except Exception as e:
            print("Subscribe send error:", e)

# Convenience: allow external creation
def create_and_start_streamer():
    streamer = AngelStreamer(TOKENS)
    streamer.start()
    return streamer
