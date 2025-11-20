from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "service": "signal"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/signal")
def sig(symbol: str = "BANKNIFTY"):
    return {"signal": "watch", "symbol": symbol}
