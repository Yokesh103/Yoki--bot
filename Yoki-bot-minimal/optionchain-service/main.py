from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "service": "optionchain"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/optionchain")
def get_chain(symbol: str = "BANKNIFTY"):
    return {"symbol": symbol, "data": "placeholder"}
