import os
import pandas as pd
import pytest
from datetime import datetime
from feature_factory.backfill.storage import Storage
from feature_factory.backfill.models import BackfillJob, BackfillChunk, BackfillStatus

@pytest.fixture
def storage(tmp_path):
    db_file = tmp_path / "test.duckdb"
    return Storage(db_path=str(db_file))

def test_create_and_get_job(storage):
    job = BackfillJob(
        id="job1",
        exchange="binance",
        symbol="BTCUSDT",
        start_time=datetime(2025, 1, 1),
        end_time=datetime(2025, 1, 2),
        status=BackfillStatus.PENDING
    )
    storage.create_job(job)
    fetched = storage.get_job_by_id("job1")
    assert fetched.id == job.id
    assert fetched.exchange == "binance"
    assert fetched.symbol == "BTCUSDT"
    assert fetched.status == BackfillStatus.PENDING

def test_get_job_not_found(storage):
    with pytest.raises(KeyError):
        storage.get_job_by_id("no_such_job")

def test_chunk_lifecycle(storage):
    # Insert a chunk row directly
    storage.conn.execute("""
        INSERT INTO chunks (id, job_id, chunk_start, chunk_end, status)
        VALUES ('chunk1','jobA','2025-01-10','2025-01-11','PENDING')
    """)
    next_chunk = storage.get_next_pending_chunk("jobA")
    assert isinstance(next_chunk, BackfillChunk)
    assert next_chunk.id == "chunk1"
    # Update its status
    storage.update_chunk_status("chunk1", BackfillStatus.COMPLETE)
    status = storage.conn.execute(
        "SELECT status FROM chunks WHERE id='chunk1'"
    ).fetchone()[0]
    assert status == BackfillStatus.COMPLETE.value

def test_get_next_pending_chunk_none(storage):
    # No chunks exist yet
    assert storage.get_next_pending_chunk("doesnt_matter") is None

def test_write_market_data(storage):
    df = pd.DataFrame({
        "price": [100, 200],
        "qty": [1, 2],
        "timestamp": [datetime(2025, 1, 1), datetime(2025, 1, 2)]
    })
    storage.write_market_data(df)
    rows = storage.conn.execute(
        "SELECT price, qty, timestamp FROM market_data ORDER BY price"
    ).fetchall()
    assert rows == [
        (100, 1, datetime(2025, 1, 1)),
        (200, 2, datetime(2025, 1, 2))
    ]
