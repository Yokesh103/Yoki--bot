from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "service": "paperexec"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/exec")
def exe(order: dict):
    return {"status": "filled", "order": order}
