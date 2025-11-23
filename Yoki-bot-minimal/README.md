
# Yoki-bot Minimal Core

Minimal core for Yoki-bot including both BANKNIFTY and NIFTY support.

## Included services

- optionchain-service (FastAPI) -> /optionchain?symbol=BANKNIFTY|NIFTY
- greeks-service (FastAPI) -> /compute
- signal-engine (FastAPI) -> /signal
- order-manager (FastAPI) -> /submit
- paper-exec (FastAPI) -> /exec

## Backtest CSV
The backtest CSV you uploaded is referenced by the services at this local path (use this path when wiring backtest loader):

`/mnt/data/Backtest Stocks Trading above Previous 20 Day High, Technical Analysis Scanner.csv`

## Run locally

```bash
docker-compose up --build
```

## Notes
- All services are placeholder stubs. Replace placeholder logic with real NSE scraping, Greeks computation and strategy rules.

signal -engine
cd signal-engine
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8100
