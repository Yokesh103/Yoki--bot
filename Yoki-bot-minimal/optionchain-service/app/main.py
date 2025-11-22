from fastapi import FastAPI
from app.option_chain_service import build_option_chain

app = FastAPI(title="Option Chain Service")

@app.get("/health")
def health():
    return {"status": "OK"}

@app.get("/test-chain")
def test_chain():
    return build_option_chain()
