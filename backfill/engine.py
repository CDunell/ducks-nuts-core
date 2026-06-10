# backfill/engine.py
import asyncio
import aiohttp
from typing import List, Dict, Optional
from pathlib import Path
import json
import time
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class BackfillJob:
    symbol: str
    start_time: int  # Unix timestamp (ms)
    end_time: int
    interval: str  # e.g., "1d", "1h"
    chunk_size: int = 1000  # Records per API call

class BinanceBackfillEngine:
    BASE_URL = "https://api.binance.com/api/v3/klines"

    def __init__(self, session: aiohttp.ClientSession, jobs: List[BackfillJob]):
        self.session = session
        self.jobs = jobs
        self.checkpoint_dir = Path(".checkpoints")
        self.checkpoint_dir.mkdir(exist_ok=True)

    async def fetch_chunk(
        self, 
        symbol: str, 
        start_time: int, 
        end_time: int, 
        interval: str
    ) -> List[List]:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": 1000,
        }
        for attempt in range(3):  # Exponential backoff
            try:
                async with self.session.get(self.BASE_URL, params=params) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    return data
            except Exception as e:
                wait = 2 ** attempt
                logger.warning(f"Retry {attempt + 1}/3 for {symbol}, waiting {wait}s", error=str(e))
                await asyncio.sleep(wait)
        raise Exception(f"Failed after 3 retries for {symbol}")

    def _get_checkpoint_path(self, job: BackfillJob) -> Path:
        return self.checkpoint_dir / f"{job.symbol}_{job.interval}.json"

    def load_checkpoint(self, job: BackfillJob) -> Optional[int]:
        """Returns last successful timestamp or None"""
        cp_path = self._get_checkpoint_path(job)
        if cp_path.exists():
            with open(cp_path) as f:
                return json.load(f).get("last_time")
        return None

    def save_checkpoint(self, job: BackfillJob, last_time: int):
        cp_path = self._get_checkpoint_path(job)
        with open(cp_path, "w") as f:
            json.dump({"last_time": last_time}, f)

    async def run_job(self, job: BackfillJob):
        current_time = self.load_checkpoint(job) or job.start_time
        symbol, interval = job.symbol, job.interval

        while current_time < job.end_time:
            chunk_end = min(
                current_time + job.chunk_size * self._interval_to_ms(interval),
                job.end_time
            )
            logger.info(f"Fetching {symbol} {interval}", start=current_time, end=chunk_end)
            
            data = await self.fetch_chunk(symbol, current_time, chunk_end, interval)
            if not data:
                break

            yield data  # Stream chunks to storage
            
            current_time = int(data[-1][0]) + 1  # Next start = last candle's open time +1ms
            self.save_checkpoint(job, current_time)

    @staticmethod
    def _interval_to_ms(interval: str) -> int:
        """Convert Binance interval (e.g., '1h') to milliseconds"""
        unit = interval[-1]
        scale = {
            "m": 60 * 1000,
            "h": 60 * 60 * 1000,
            "d": 24 * 60 * 60 * 1000,
        }[unit]
        return int(interval[:-1]) * scale

async def backfill(jobs: List[BackfillJob]):
    async with aiohttp.ClientSession() as session:
        engine = BinanceBackfillEngine(session, jobs)
        for job in jobs:
            async for chunk in engine.run_job(job):
                yield job.symbol, chunk