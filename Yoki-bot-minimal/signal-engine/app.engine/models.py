from pydantic import BaseModel
from typing import Any, Dict, Optional, List

class IndicatorSnapshot(BaseModel):
    adx14: float
    rsi14: float
    atr14: float
    ivrank: float
    vix: Optional[float] = None
    is_expiry_thursday: bool = False
    time_str: Optional[str] = None  # "10:32"

class InstrumentRow(BaseModel):
    instrument_key: str
    strike: float
    opt_type: str  # "CE"/"PE"
    expiry: str

class DecideRequest(BaseModel):
    underlying: str
    expiry: str
    instruments: List[InstrumentRow]
    indicators: IndicatorSnapshot
    spot: float

class DecisionResult(BaseModel):
    action: str  # TRADE | NO_TRADE
    strategy: Optional[str]
    reason: Optional[str]
    trade_payload: Optional[Dict[str, Any]]
    decision_id: Optional[str]
