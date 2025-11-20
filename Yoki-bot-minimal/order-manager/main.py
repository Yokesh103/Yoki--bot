from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "service": "ordermanager"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/submit")
def sub(order: dict):
    return {"accepted": True, "order": order}
