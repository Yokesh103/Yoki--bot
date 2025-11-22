```python
"""Builds a list of strikes centered at atm.
wings = number of strikes on each side of ATM
"""
step = STRIKE_STEP_BY_INDEX.get(index.upper(), 50)
strikes = [atm + i * step for i in range(-wings, wings + 1)]
# ensure unique sorted
strikes = sorted(list(set(strikes)))
return strikes
```


---


## services/optionchain/app/api.py


```python
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .models import OptionChainResponse
from .service import MockMarketDataProvider, detect_atm, build_strike_range


router = APIRouter()


# use provider instance (easy to swap for a real provider)
PROVIDER = MockMarketDataProvider()


@router.get("/optionchain", response_model=OptionChainResponse)
async def get_optionchain(index: str = Query("NIFTY", description="Index name, e.g., NIFTY or BANKNIFTY"),
wings: Optional[int] = Query(10, ge=1, le=40, description="how many strikes each side of ATM")):
index = index.upper()
# fetch spot
spot = await PROVIDER.get_spot(index)
if spot is None:
raise HTTPException(status_code=502, detail="spot unavailable")


# detect ATM
atm = await detect_atm(spot, index)


# build strikes
strikes = await build_strike_range(atm, index, wings=wings)


# get expiry
expiry = await PROVIDER.get_expiry(index)


# option chain
ce, pe = await PROVIDER.get_option_chain(index, atm, strikes)


return {
"index": index,
"spot": float(spot),
"atm_strike": atm,
"expiry": expiry,
"strikes": strikes,
"ce": ce,
"pe": pe,
}


@router.get("/spot")
async def get_spot(index: str = Query("NIFTY")):
s = await PROVIDER.get_spot(index.upper())
return {"index": index.upper(), "spot": s}


@router.get("/atm")
async def get_atm(index: str = Query("NIFTY")):
s = await PROVIDER.get_spot(index.upper())
atm = await detect_atm(s, index.upper())
return {"index": index.upper(), "spot": s, "atm": atm}
```


