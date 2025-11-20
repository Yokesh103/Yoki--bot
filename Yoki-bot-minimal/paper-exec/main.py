# paper-exec/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import time, uuid

app = FastAPI(title="paper-exec")

class ExecReq(BaseModel):
    order_id: str
    legs: list
    qty: int = 25
    slippage_pct: float = 0.2

@app.post("/exec")
async def exec_order(req: ExecReq):
    # Very simple fill simulation: echo back with simulated fill prices
    fills = []
    for leg in req.legs:
        # leg example: {"strike":59000,"side":"BUY","option":"CE","price":400}
        price = leg.get("price", 100)
        slippage = price * (req.slippage_pct / 100.0)
        fill_price = round(price + (slippage if leg.get("side","BUY")=="BUY" else -slippage), 2)
        fills.append({
            "strike": leg.get("strike"),
            "side": leg.get("side"),
            "option": leg.get("option"),
            "fill_price": fill_price,
            "qty": req.qty
        })
    resp = {
        "order_id": req.order_id,
        "fills": fills,
        "status": "filled",
        "timestamp": time.time()
    }
    return resp
