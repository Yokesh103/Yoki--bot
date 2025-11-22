# app/config.py

UPSTOX_API_KEY = "a0381d7c-d618-4490-b4ad-209a61a96126"
UPSTOX_REDIRECT_URI = "http://localhost:5000/upstox/callback"

# ALWAYS put the REAL working token here (no prefixes, no text)
UPSTOX_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI4QkFMRUgiLCJqdGkiOiI2OTIxOTU2MWNmYzJkNzQ4ZWQwN2MyZDgiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MzgwODYwOSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYzODQ4ODAwfQ.zB3B2fuCp13ji3BOxfKnIojo890FV6211LxEo6lG88k"

# Standardised index names for Upstox instruments
INDICES = ["NIFTY 50", "Nifty Bank"]

DB_PATH = "data/options.db"
