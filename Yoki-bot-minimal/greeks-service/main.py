from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "service": "greeks"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/compute")
def compute(payload: dict):
    return {'delta': 0.5, 'gamma': 0.01, 'theta': -0.02, 'vega': 0.1}
