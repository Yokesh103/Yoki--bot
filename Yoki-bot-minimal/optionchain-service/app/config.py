# app/config.py

UPSTOX_API_KEY = "a0381d7c-d618-4490-b4ad-209a61a96126"
UPSTOX_REDIRECT_URI = "http://localhost:5000/upstox/callback"

# ALWAYS put the REAL working token here (no prefixes, no text)
UPSTOX_ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI4QkFMRUgiLCJqdGkiOiI2OTI3NGJiNjhjZDgwMjRlMjQ1NWU1ZjgiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2NDE4Mjk2NiwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzY0MTk0NDAwfQ.JU1jUk1UI5P4IPYH7j-fbXSHB-smD8ni7Igl3ZhYap0"

# Standardised index names for Upstox instruments
INDICES = ["NIFTY 50", "Nifty Bank"]

DB_PATH = "data/options.db"
