```python
app = FastAPI(title="OptionChain Service", version="1.0")


app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_methods=["*"],
allow_headers=["*"],
)


app.include_router(api_router, prefix="")


@app.get("/health")
async def health():
return {"status": "ok"}


if __name__ == '__main__':
uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```


---


## services/optionchain/app/models.py


```python
from pydantic import BaseModel
from typing import List, Optional


class OptionLeg(BaseModel):
strike: int
type: str # 'CE' or 'PE'
ltp: float
oi: int


class OptionChainResponse(BaseModel):
index: str
spot: float
atm_strike: int
expiry: str
strikes: List[int]
ce: List[OptionLeg]
pe: List[OptionLeg]
```