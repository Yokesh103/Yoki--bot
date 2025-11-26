import requests

ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI4QkFMRUgiLCJqdGkiOiI2OTI3NGJiNjhjZDgwMjRlMjQ1NWU1ZjgiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2NDE4Mjk2NiwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzY0MTk0NDAwfQ.JU1jUk1UI5P4IPYH7j-fbXSHB-smD8ni7Igl3ZhYap0"
r = requests.get(
    "https://api.upstox.com/v2/user/profile",
    headers={
        "Accept": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
)

print(r.status_code, r.json())



