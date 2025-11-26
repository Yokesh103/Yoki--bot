import sqlite3
from pathlib import Path

DB_PATH = Path("data/options.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("TOTAL ROWS:", cur.execute("SELECT COUNT(*) FROM instruments").fetchone()[0])

print("\nUNDERLYINGS:")
for r in cur.execute("SELECT DISTINCT underlying FROM instruments LIMIT 10"):
    print(r[0])

print("\nNIFTY EXPIRIES:")
for r in cur.execute("SELECT DISTINCT expiry FROM instruments WHERE underlying='NIFTY'"):
    print(r[0])

print("\nBANKNIFTY EXPIRIES:")
for r in cur.execute("SELECT DISTINCT expiry FROM instruments WHERE underlying='BANKNIFTY'"):
    print(r[0])

conn.close()
