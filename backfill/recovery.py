# backfill/recovery.py

from .storage import Storage
from .models import BackfillStatus

def list_failed_chunks(storage: Storage, job_id: str) -> list[str]:
    """
    Returns a list of chunk IDs that are in FAILED status.
    """
    rows = storage.conn.execute(
        "SELECT id FROM chunks WHERE job_id = ? AND status = ? ORDER BY chunk_start",
        [job_id, BackfillStatus.FAILED.value]
    ).fetchall()
    return [r[0] for r in rows]

def reset_failed_chunks(storage: Storage, job_id: str) -> int:
    """
    Resets all FAILED chunks back to PENDING. Returns the number of chunks reset.
    """
    storage.conn.execute(
        "UPDATE chunks SET status = ? WHERE job_id = ? AND status = ?",
        [BackfillStatus.PENDING.value, job_id, BackfillStatus.FAILED.value]
    )
    # Return how many were reset (now pending that were previously failed)
    return storage.conn.execute(
        "SELECT COUNT(*) FROM chunks WHERE job_id = ? AND status = ?",
        [job_id, BackfillStatus.PENDING.value]
    ).fetchone()[0]
