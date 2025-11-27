def extract_tick_data(raw):
    return {
        "instrument_key": raw.get("instrument_key"),
        "ltp": raw.get("last_traded_price"),
        "oi": raw.get("oi"),
        "volume": raw.get("volume"),
        "timestamp": raw.get("timestamp"),
    }
