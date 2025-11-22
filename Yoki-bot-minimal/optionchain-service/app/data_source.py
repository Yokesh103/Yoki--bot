from abc import ABC, abstractmethod
from typing import Dict, Any, List
import requests
from app.config import UPSTOX_ACCESS_TOKEN

UPSTOX_QUOTES_URL = "https://api.upstox.com/v2/market-quote/quotes"


class MarketDataSource(ABC):
    @abstractmethod
    def get_snapshot(self, instrument_keys: List[str]) -> Dict[str, Any]:
        raise NotImplementedError


class RestMarketDataSource(MarketDataSource):
    def get_snapshot(self, instrument_keys: List[str]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI4QkFMRUgiLCJqdGkiOiI2OTIxOTU2MWNmYzJkNzQ4ZWQwN2MyZDgiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2MzgwODYwOSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYzODQ4ODAwfQ.zB3B2fuCp13ji3BOxfKnIojo890FV6211LxEo6lG88k}",
            "Accept": "application/json",
        }

        params = {
            "instrument_key": ",".join(instrument_keys)
        }

        response = requests.get(
            UPSTOX_QUOTES_URL,
            headers=headers,
            params=params
        )

        response.raise_for_status()
        return response.json()
