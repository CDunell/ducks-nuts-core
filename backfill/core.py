# ⚠️ PATCHED: 2025-07-23
# Task: Add rich live chunk logging, concurrency, and slowness diagnostics
# Source file ID: file-DVDopfz218anCUzqiorXyS

import time
import asyncio
from collections import deque
from rich.live import Live
from rich.table import Table

from .config import settings
from .storage import Storage
from .clients import BinanceClient
from .transform import transform_ohlcv
from .models import BackfillStatus

class BackfillEngine:
    """
    Orchestrates fetching, transforming, and storing OHLCV data by chunk.
    Now uses Rich to display only the last 5 chunks in-place.
    """

    MAX_CONCURRENCY = 4

    def __init__(self, storage: Storage = None, client=None):
        self.storage = storage or Storage()
        self.client  = client or BinanceClient()
        self.chunk_log = deque(maxlen=5)

    async def fetch_store_chunk(self, job_id: str, chunk):
        start_ts = time.perf_counter()
        try:
            job = self.storage.get_job_by_id(job_id)
            raw = await self.client.fetch_ohlcv(
                job.symbol,
                start_time=chunk.chunk_start,
                end_time=chunk.chunk_end,
            )
            df = transform_ohlcv(raw)
            if df.empty:
                self.storage.update_chunk_status(chunk.id, BackfillStatus.FAILED)
                self.chunk_log.append((chunk.id[:8], 0, 0.0, '⚠️ Empty'))
                return
            self.storage.write_market_data(df)
            self.storage.update_chunk_status(chunk.id, BackfillStatus.COMPLETE)
            duration = time.perf_counter() - start_ts
            self.chunk_log.append((chunk.id[:8], len(df), duration, "✓"))
        except Exception as e:
            self.storage.update_chunk_status(chunk.id, BackfillStatus.FAILED)
            self.chunk_log.append((chunk.id[:8], 0, 0.0, "✗ " + str(e).splitlines()[0][:40]))

    async def run(self, job_id: str):
        print(f"▶️ Starting backfill engine for job: {job_id}")
        with Live(refresh_per_second=3) as live:
            while True:
                chunks = []
                for _ in range(self.MAX_CONCURRENCY):
                    chunk = self.storage.get_next_pending_chunk(job_id)
                    if not chunk:
                        break
                    self.storage.update_chunk_status(chunk.id, BackfillStatus.RUNNING)
                    chunks.append(chunk)

                if not chunks:
                    break

                tasks = [self.fetch_store_chunk(job_id, chunk) for chunk in chunks]
                await asyncio.gather(*tasks)

                table = Table(title="Recent Chunks", expand=True)
                table.add_column("Chunk", justify="left")
                table.add_column("Rows", justify="right")
                table.add_column("Time (s)", justify="right")
                table.add_column("Status", justify="left")

                for cid, rows, t, s in self.chunk_log:
                    table.add_row(cid, str(rows), f"{t:.2f}", s)

                live.update(table)

                if not settings.TESTING:
                    await asyncio.sleep(0.2)

        try:
            await self.client.close()
        except Exception:
            pass
