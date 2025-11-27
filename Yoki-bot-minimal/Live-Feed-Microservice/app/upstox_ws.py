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
