# ⚠️ PATCHED: 2025-07-23
# Task: Eliminate client reuse to prevent closed-client errors across engines
# Source file ID: file-DT2iLS1uF8b8kGBQbmsHTG

import uuid
import asyncio
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .storage import Storage
from .models import BackfillJob, BackfillStatus
from .chunker import generate_chunks
from realtime.tick_processor_zmq import PINNED_SYMBOLS

async def backfill_top_symbols(
    limit: int = None,
    years: int = 2,
    chunk_hours: int = 6,
    db_path: str = None
):
    """
    Run backfill jobs for all pinned symbols over the past `years` years.
    """
    storage = Storage(db_path=db_path)
    end = datetime.utcnow()
    start = end - relativedelta(years=years)

    for symbol in [s.upper() for s in PINNED_SYMBOLS]:
        from .core import BackfillEngine
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
