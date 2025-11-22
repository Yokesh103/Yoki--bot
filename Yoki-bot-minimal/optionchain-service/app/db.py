import sqlite3
from pathlib import Path

DB_PATH = Path("data/options.db")
DB_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS option_snapshots (
        ts TEXT,
        underlying TEXT,
        expiry TEXT,
        strike REAL,
        opt_type TEXT,  -- 'CE' or 'PE'
        ltp REAL,
        oi INTEGER
    )
    """)
    conn.commit()
