# optionchain-service/main.py
from fastapi import FastAPI, Query
import requests, json, datetime, time
from functools import lru_cache

app = FastAPI(title="optionchain-service")

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "*/*",
    "Connection": "keep-alive"
}

SESSION = requests.Session()

# -----------------------------------
# Helper: Refresh cookies every 6 min
# -----------------------------------
def refresh_cookies():
    try:
        SESSION.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=5)
    except:
        pass

refresh_cookies()

# Refresh cookies every 6 minutes
LAST_COOKIE_TIME = time.time()

def ensure_cookies():
    global LAST_COOKIE_TIME
    if time.time() - LAST_COOKIE_TIME > 360:
        refresh_cookies()
        LAST_COOKIE_TIME = time.time()

# -----------------------------------
# Get option chain URL based on symbol
# -----------------------------------
def get_chain_url(symbol: str):
    if symbol == "BANKNIFTY":
        return "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY"
    else:
        return "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

# -----------------------------------
# Fetch Option Chain (REAL)
# -----------------------------------
def fetch_option_chain(symbol: str):
    ensure_cookies()
    url = get_chain_url(symbol)

    resp = SESSION.get(url, headers=NSE_HEADERS, timeout=10)
    data = resp.json()

    # Clean structure
    underlying = data["records"]["underlyingValue"]
    expiry = data["records"]["expiryDates"][0]  # nearest weekly expiry
    strikes = data["records"]["data"]

    cleaned = []
    for item in strikes:
        strike = item["strikePrice"]

        ce = item.get("CE", {})
        pe = item.get("PE", {})

        cleaned.append({
            "strike": strike,
            "ce_ltp": ce.get("lastPrice"),
            "pe_ltp": pe.get("lastPrice"),
            "ce_oi": ce.get("openInterest"),
            "pe_oi": pe.get("openInterest")
        })

    return {
        "symbol": symbol,
        "spot": underlying,
        "expiry": expiry,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "strikes": cleaned
    }

# -----------------------------------
# API Endpoint
# -----------------------------------
@app.get("/optionchain")
async def optionchain(symbol: str = Query("BANKNIFTY")):
    try:
        out = fetch_option_chain(symbol.upper())
        return {"status": "ok", "data": out}
    except Exception as e:
        return {"status": "error", "message": str(e)}
