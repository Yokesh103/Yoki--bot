# order-manager/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid, time

app = FastAPI(title="order-manager")
orders = {}  # in-memory order store for minimal core

class OrderReq(BaseModel):
    symbol: str
    strategy: str
    legs: list
    qty: Optional[int] = 25
    limit: Optional[float] = None

@app.post("/createOrder")
async def create_order(req: OrderReq):
    oid = str(uuid.uuid4())
    orders[oid] = {
        "id": oid,
        "symbol": req.symbol,
        "strategy": req.strategy,
        "legs": req.legs,
        "qty": req.qty,
        "limit": req.limit,
        "status": "submitted",
        "submitted_at": time.time()
    }
    # Simulate immediate routing to paper-exec in production; for minimal core leave as submitted
    return {"status":"accepted", "order_id": oid}

@app.get("/order/{order_id}")
async def get_order(order_id: str):
    o = orders.get(order_id)
    if not o:
        raise HTTPException(status_code=404, detail="order not found")
    return o
