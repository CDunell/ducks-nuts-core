import pytest
from feature_factory.backfill.monitor import get_job_progress, format_progress_report
from feature_factory.backfill.storage import Storage
from feature_factory.backfill.models import BackfillJob, BackfillChunk, BackfillStatus
from datetime import datetime

@pytest.fixture
def storage(tmp_path):
    db = Storage(db_path=str(tmp_path / "test.duckdb"))
    # make a job + 4 chunks
    job = BackfillJob(
        id="j1", exchange="binance", symbol="BTCUSDT",
        start_time=datetime(2025,1,1), end_time=datetime(2025,1,2),
        status=BackfillStatus.PENDING
    )
    db.create_job(job)
    times = [datetime(2025,1,1), datetime(2025,1,1,6),
             datetime(2025,1,1,12), datetime(2025,1,1,18)]
    for i, t in enumerate(times, start=1):
        db.conn.execute(
            "INSERT INTO chunks (id, job_id, chunk_start, chunk_end, status) VALUES (?,?,?,?,?)",
            [f"c{i}", "j1", t, t, BackfillStatus.PENDING.value]
        )
    # mark two complete, one failed
    db.conn.execute("UPDATE chunks SET status = ? WHERE id = ?", [BackfillStatus.COMPLETE.value, "c1"])
    db.conn.execute("UPDATE chunks SET status = ? WHERE id = ?", [BackfillStatus.COMPLETE.value, "c2"])
    db.conn.execute("UPDATE chunks SET status = ? WHERE id = ?", [BackfillStatus.FAILED.value, "c3"])
    return db

def test_get_job_progress(storage):
    prog = get_job_progress(storage, "j1")
    assert prog["total"] == 4
    assert prog["complete"] == 2
    assert prog["failed"] == 1
    assert prog["pending"] == 1
    assert prog["percent_complete"] == 50.0

def test_format_progress_report():
    rep = format_progress_report({
        "total": 4, "complete": 2, "failed": 1, "pending": 1, "percent_complete": 50.0
    })
    assert "2/4 complete" in rep
    assert "1 failed" in rep
    assert "(50.0% done)" in rep
