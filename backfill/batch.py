# ⚠️ PATCHED: 2025-07-23
# Task: Eliminate client reuse to prevent closed-client errors across engines
# Source file ID: file-DT2iLS1uF8b8kGBQbmsHTG

import uuid
import asyncio
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .clients import BinanceClient
from .storage import Storage
from .models import BackfillJob, BackfillStatus
from .chunker import generate_chunks

async def backfill_top_symbols(
    limit: int = 10,
    years: int = 2,
    chunk_hours: int = 6,
    db_path: str = None
):
    """
    Automatically create and run backfill jobs for the top `limit`
    Binance symbols by 24hr volume over the past `years` years.
    """
    storage = Storage(db_path=db_path)
    client = BinanceClient()
    tickers = await client.fetch_24hr_tickers()
    usdt = [t for t in tickers if t["symbol"].endswith("USDT")]
    sorted_pairs = sorted(
        usdt,
        key=lambda t: float(t["quoteVolume"]),
        reverse=True
    )[:limit]

    end = datetime.utcnow()
    start = end - relativedelta(years=years)

    for info in sorted_pairs:
        from .core import BackfillEngine
        symbol = info["symbol"]
        job_id = str(uuid.uuid4())
        job = BackfillJob(
            id=job_id,
            exchange="binance",
            symbol=symbol,
            start_time=start,
            end_time=end,
            status=BackfillStatus.PENDING,
        )
        storage.create_job(job)
        generate_chunks(storage, job_id, chunk_hours)
        engine = BackfillEngine(storage)
        await engine.run(job_id)
