# greeks-service/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import numpy as np
from py_vollib.black.greeks.analytical import delta as bs_delta, gamma as bs_gamma, theta as bs_theta, vega as bs_vega, rho as bs_rho
from py_vollib.black.implied_volatility import implied_volatility as bs_iv
from py_vollib.black_scholes.implied_volatility import implied_volatility as bs_equity_iv
from py_vollib.black_scholes.greeks.analytical import delta as eq_delta, gamma as eq_gamma, theta as eq_theta, vega as eq_vega, rho as eq_rho

import math

app = FastAPI(title="greeks-service", version="1.0.0")


# -------------------------------
# Request model
# -------------------------------
class GreeksRequest(BaseModel):
    underlying: float
    strike: float
    option_price: float
    expiry: str
    option_type: str   # CE / PE
    model: str = "black76"  # black76 (default) or bs


# -------------------------------
# Helper: convert expiry to TTE
# -------------------------------
def compute_tte(expiry_str: str):
    expiry = datetime.fromisoformat(expiry_str)
    now = datetime.utcnow()
    diff_seconds = (expiry - now).total_seconds()
    if diff_seconds <= 0:
        return 0.00001
    return diff_seconds / (365 * 24 * 60 * 60)


# -------------------------------
# Greeks response builder
# -------------------------------
def safe_round(x):
    try:
        return round(float(x), 6)
    except:
        return None


# -------------------------------
# Main Greeks compute
# -------------------------------
def compute_greeks_real(data: GreeksRequest):
    S = float(data.underlying)
    K = float(data.strike)
    price = float(data.option_price)
    option_type = data.option_type.upper()
    model = data.model.lower()

    is_call = True if option_type == "CE" else False

    t = compute_tte(data.expiry)
    r = 0.0  # NSE index options have no risk-free rate effect for Black-76

    # -------------------------------
    # 1. IMPLIED VOLATILITY
    # -------------------------------
    try:
        if model == "black76":
            iv = bs_iv(price, S, K, r, t, "c" if is_call else "p")
        else:
            iv = bs_equity_iv(price, S, K, r, t, "c" if is_call else "p")
    except Exception:
        iv = None

    if iv is None or iv <= 0:
        return {
            "error": "IV could not be computed",
            "iv": None,
            "delta": None,
            "gamma": None,
            "theta": None,
            "vega": None,
            "rho": None,
            "used_model": model,
            "ttm_years": safe_round(t)
        }

    # -------------------------------
    # 2. GREEKS
    # -------------------------------
    if model == "black76":
        d = bs_delta("c" if is_call else "p", S, K, r, t, iv)
        g = bs_gamma("c" if is_call else "p", S, K, r, t, iv)
        th = bs_theta("c" if is_call else "p", S, K, r, t, iv)
        v = bs_vega("c" if is_call else "p", S, K, r, t, iv)
        rh = bs_rho("c" if is_call else "p", S, K, r, t, iv)
    else:
        d = eq_delta("c" if is_call else "p", S, K, t, iv)
        g = eq_gamma("c" if is_call else "p", S, K, t, iv)
        th = eq_theta("c" if is_call else "p", S, K, t, iv)
        v = eq_vega("c" if is_call else "p", S, K, t, iv)
        rh = eq_rho("c" if is_call else "p", S, K, t, iv)

    return {
        "iv": safe_round(iv),
        "delta": safe_round(d),
        "gamma": safe_round(g),
        "theta": safe_round(th),
        "vega": safe_round(v),
        "rho": safe_round(rh),
        "used_model": model,
        "ttm_years": safe_round(t)
    }


# -------------------------------
# API Endpoints
# -------------------------------
@app.get("/health")
async def health():
    return {"status": "alive", "service": "greeks-service"}


@app.post("/compute")
async def compute(req: GreeksRequest):
    try:
        result = compute_greeks_real(req)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
