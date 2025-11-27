# CENTRAL LIVE CACHE

TICK_CACHE = {}

def update_tick(instrument_key: str, data: dict):
    TICK_CACHE[instrument_key] = data

def get_tick(instrument_key: str):
    return TICK_CACHE.get(instrument_key)

def get_all_ticks():
    return TICK_CACHE
