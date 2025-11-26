# optionchain-service/app/init_instruments_db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "options.db"

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS instruments (
            instrument_key TEXT PRIMARY KEY,
            underlying     TEXT NOT NULL,
            segment        TEXT NOT NULL,
            instrument_type TEXT NOT NULL,
            strike         REAL,
            opt_type       TEXT,
            expiry         TEXT NOT NULL
        )
        """
    )

    # Indexes to make lookups fast
    cur.execute("CREATE INDEX IF NOT EXISTS idx_instruments_underlying ON instruments(underlying)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_instruments_expiry ON instruments(expiry)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_instruments_underlying_expiry ON instruments(underlying, expiry)")

    conn.commit()
    conn.close()
    print(f"Initialized DB at: {DB_PATH}")

if __name__ == "__main__":
    init_db()
