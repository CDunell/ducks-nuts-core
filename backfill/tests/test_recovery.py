from feature_factory.backfill.recovery import list_failed_chunks, reset_failed_chunks
from feature_factory.backfill.storage import Storage
from feature_factory.backfill.models import BackfillJob, BackfillChunk, BackfillStatus
from datetime import datetime
import pytest

@pytest.fixture
def storage(tmp_path):
    db = Storage(db_path=str(tmp_path / "test.duckdb"))
    job = BackfillJob(
        id="j1", exchange="binance", symbol="ETHUSDT",
        start_time=datetime(2025,1,1), end_time=datetime(2025,1,2),
        status=BackfillStatus.PENDING
    )
    db.create_job(job)
    # insert chunks c1 FAILED, c2 COMPLETE, c3 FAILED
    for cid, status in [("c1","FAILED"),("c2","COMPLETE"),("c3","FAILED")]:
        db.conn.execute(
            "INSERT INTO chunks (id,job_id,chunk_start,chunk_end,status) VALUES (?,?,?,?,?)",
            [cid, "j1", datetime(2025,1,1), datetime(2025,1,1), status]
        )
    return db

def test_list_failed_chunks(storage):
    failed = list_failed_chunks(storage, "j1")
    assert set(failed) == {"c1", "c3"}

def test_reset_failed_chunks(storage):
    count = reset_failed_chunks(storage, "j1")
    assert count == 2
    # now no FAILED remain
    assert list_failed_chunks(storage, "j1") == []
