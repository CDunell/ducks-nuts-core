import pytest
from datetime import datetime
from feature_factory.backfill.models import BackfillStatus, BackfillJob, BackfillChunk

def test_status_enum():
    assert BackfillStatus.PENDING.value == "PENDING"

def test_backfill_job_valid():
    job = BackfillJob(
        id="job1",
        exchange="binance",
        symbol="BTCUSDT",
        start_time=datetime(2025, 1, 1),
        end_time=datetime(2025, 1, 2),
        status=BackfillStatus.PENDING
    )
    assert job.symbol == "BTCUSDT"

def test_backfill_job_invalid_dates():
    with pytest.raises(ValueError):
        BackfillJob(
            id="job1",
            exchange="binance",
            symbol="BTCUSDT",
            start_time="not-a-date",
            end_time=datetime(2025, 1, 2),
            status=BackfillStatus.PENDING
        )

def test_backfill_chunk_valid():
    chunk = BackfillChunk(
        id="chunk1",
        job_id="job1",
        chunk_start=datetime(2025, 1, 1, 0, 0),
        chunk_end=datetime(2025, 1, 1, 6, 0),
        status=BackfillStatus.PENDING
    )
    assert chunk.job_id == "job1"

def test_backfill_chunk_invalid_dates():
    with pytest.raises(ValueError):
        BackfillChunk(
            id="chunk1",
            job_id="job1",
            chunk_start="bad-date",
            chunk_end=datetime(2025, 1, 1, 6, 0),
            status=BackfillStatus.PENDING
        )
