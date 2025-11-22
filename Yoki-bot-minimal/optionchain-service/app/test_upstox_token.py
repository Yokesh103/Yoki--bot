import requests

ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI4QkFMRUgiLCJqdGkiOiI2OTIxOTU2MWNmYzJkNzQ4ZWQwN2MyZDgiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MzgwODYwOSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYzODQ4ODAwfQ.zB3B2fuCp13ji3BOxfKnIojo890FV6211LxEo6lG88k"
r = requests.get(
    "https://api.upstox.com/v2/user/profile",
    headers={
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
)

print(r.status_code, r.json())



