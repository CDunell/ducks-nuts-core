# ⚠️ PATCHED: 2025-07-23
# Task: Add diagnostic logging to fetch_ohlcv and skip empty symbols in 24hr ticker fetch
# Source file ID: file-8TXrWxQZ7XyvnKjzwepSQC

import httpx
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List, Optional

from .config import settings

class BaseExchangeClient(ABC):
    """
    Abstract base class for exchange clients.
    """
    @abstractmethod
    async def fetch_ohlcv(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        interval: str = "1m",
        limit: int = 1000,
    ) -> List[List[Any]]:
        """
        Fetch OHLCV data between start_time and end_time.
        """
        ...

class BinanceClient(BaseExchangeClient):
    BASE_URL = "https://api.binance.com/api/v3/klines"
    TICKER_URL = "https://api.binance.com/api/v3/ticker/24hr"

    def __init__(self, base_url: Optional[str] = None):
        if settings.TESTING:
            api_key = settings.BINANCE_TESTNET_API_KEY
            api_secret = settings.BINANCE_TESTNET_API_SECRET
        else:
            api_key = settings.BINANCE_API_KEY
            api_secret = settings.BINANCE_API_SECRET

        if not api_key or not api_secret:
            raise RuntimeError("Binance API credentials not set")

        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url or self.BASE_URL
        self.client = httpx.AsyncClient()

    async def fetch_ohlcv(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        interval: str = "1m",
        limit: int = 1000,
    ) -> List[List[Any]]:
        klines = []
        epoch = datetime(1970, 1, 1)
        start_ts = int((start_time - epoch).total_seconds() * 1000)
        end_ts   = int((end_time   - epoch).total_seconds() * 1000)
        interval_ms = self._interval_to_milliseconds(interval)

        while True:
            params = {
                "symbol":    symbol,
                "interval":  interval,
                "startTime": start_ts,
                "endTime":   end_ts,
                "limit":     limit,
            }
            print(f"[DEBUG] Requesting {symbol} from {start_time} to {end_time}")
            resp = await self.client.get(self.base_url, params=params)
            resp.raise_for_status()
            batch = resp.json()
            print(f"[DEBUG] Received {len(batch)} rows for {symbol}")
            if not batch:
                break
            klines.extend(batch)
            if len(batch) < limit:
                break
            last_ts = batch[-1][0]
            start_ts = last_ts + interval_ms

        return klines

    async def fetch_24hr_tickers(self) -> List[dict]:
        resp = await self.client.get(self.TICKER_URL)
        resp.raise_for_status()
        data = resp.json()
        return [d for d in data if d.get('lastPrice') not in ('0', '0.00000000')]

    @staticmethod
    def _interval_to_milliseconds(interval: str) -> int:
        unit = interval[-1]
        amount = int(interval[:-1])
        if unit == "m":
            return amount * 60 * 1000
        if unit == "h":
            return amount * 60 * 60 * 1000
        if unit == "d":
            return amount * 24 * 60 * 60 * 1000
        if unit == "w":
            return amount * 7 * 24 * 60 * 60 * 1000
        raise ValueError(f"Unknown interval unit: {unit}")

    async def close(self) -> None:
        await self.client.aclose()
