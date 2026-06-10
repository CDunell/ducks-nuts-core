import pytest
import asyncio
from datetime import datetime
import pandas as pd

from feature_factory.backfill.storage import Storage
from feature_factory.backfill.core import BackfillEngine
from feature_factory.backfill.models import BackfillJob, BackfillStatus

class DummyClient:
    def __init__(self, data):
        self.data = data
    async def fetch_ohlcv(self, symbol, start_time, end_time, **kwargs):
        return self.data

@pytest.fixture
def storage(tmp_path):
    db_file = tmp_path / "test.duckdb"
    return Storage(db_path=str(db_file))

@pytest.mark.asyncio
async def test_engine_run_end_to_end(storage):
    # prepare job
    job_id = "job1"
    start = datetime(2025, 1, 1, 0, 0)
    end = datetime(2025, 1, 1, 0, 1)
    job = BackfillJob(
        id=job_id, exchange="binance", symbol="TEST",
        start_time=start, end_time=end, status=BackfillStatus.PENDING
    )
    storage.create_job(job)

    # insert one pending chunk covering the job range
    chunk_id = "chunk1"
    storage.conn.execute(
        "INSERT INTO chunks (id, job_id, chunk_start, chunk_end, status) VALUES (?, ?, ?, ?, ?)",
        [chunk_id, job_id, start, end, BackfillStatus.PENDING.value]
    )

    # dummy OHLCV data at the exact timestamp
    raw = [[1609459200000, "1", "1", "1", "1", "1", 1609459260000, "0", 0, "0", "0", "0"]]
    client = DummyClient(raw)
    engine = BackfillEngine(storage, client)

    # run
    await engine.run(job_id)

    # chunk status updated
    status = storage.conn.execute(
        "SELECT status FROM chunks WHERE id = ?", [chunk_id]
    ).fetchone()[0]
    assert status == BackfillStatus.COMPLETE.value

    # market_data table has expected row
    df = pd.DataFrame(storage.conn.execute(
        "SELECT open, high, low, close, volume FROM market_data"
    ).fetchall(), columns=["open", "high", "low", "close", "volume"])
    assert df.to_dict("records") == [{"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1.0}]
