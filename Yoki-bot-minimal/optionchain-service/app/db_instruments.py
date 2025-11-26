import sqlite3
from typing import List, Dict, Optional

DB_PATH = "data/options.db"


def get_instruments_from_db(underlying: str, expiry: Optional[str] = None) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if expiry:
        cur.execute("""
            SELECT instrument_key, strike, opt_type, expiry, underlying
            FROM instruments
            WHERE underlying = ? AND expiry = ?
        """, (underlying, expiry))
    else:
        cur.execute("""
            SELECT instrument_key, strike, opt_type, expiry, underlying
            FROM instruments
            WHERE underlying = ?
        """, (underlying,))

    rows = cur.fetchall()
    conn.close()

    return [dict(r) for r in rows]

def get_expiries_for_underlying(underlying: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT expiry
        FROM instruments
        WHERE underlying = ?
        ORDER BY expiry ASC
    """, (underlying,))

    rows = cur.fetchall()
    conn.close()

    return [r[0] for r in rows]

