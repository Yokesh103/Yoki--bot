from fastapi import FastAPI, Request
import requests

app = FastAPI()

API_KEY = "a0381d7c-d618-4490-b4ad-209a61a96126"
API_SECRET = "PASTE_YOUR_API_SECRET"
REDIRECT_URI = "http://localhost:5000/upstox/callback"


@app.get("/upstox/callback")
async def upstox_callback(request: Request):
    code = request.query_params.get("code")

    url = "https://api.upstox.com/v2/login/authorization/token"

    payload = {
        "code": code,
        "client_id": API_KEY,
        "client_secret": API_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(url, data=payload, headers=headers)

    return r.json()
