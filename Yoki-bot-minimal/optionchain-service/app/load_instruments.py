import sqlite3
import requests
from pathlib import Path
from app.config import UPSTOX_ACCESS_TOKEN

DB_PATH = Path("data/options.db")
UPSTOX_INSTRUMENTS_URL = "https://api.upstox.com/v2/instruments"


def load_instruments():
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {UPSTOX_ACCESS_TOKEN}",
    }

    print("Fetching instruments from Upstox...")
    resp = requests.get(UPSTOX_INSTRUMENTS_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    payload = resp.json()

    instruments = payload.get("data", payload)
    print(f"Received {len(instruments)} instruments")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    inserted = 0

    for ins in instruments:
        # Filter only options
        if ins.get("instrument_type") not in ("OPTIDX", "OPTSTK"):
            continue

        instrument_key = ins.get("instrument_key")
        underlying = ins.get("underlying_symbol")
        strike = ins.get("strike_price")
        opt_type = ins.get("option_type")
        expiry = ins.get("expiry")
        segment = ins.get("segment")

        if not all([instrument_key, underlying, expiry]):
            continue

        cur.execute("""
            INSERT OR REPLACE INTO instruments (
                instrument_key, underlying, segment, instrument_type,
                strike, opt_type, expiry
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            instrument_key,
            underlying,
            segment,
            ins.get("instrument_type"),
            strike,
            opt_type,
            expiry
        ))

        inserted += 1

    conn.commit()
    conn.close()
    print(f"Inserted {inserted} option instruments into DB")


if __name__ == "__main__":
    load_instruments()
