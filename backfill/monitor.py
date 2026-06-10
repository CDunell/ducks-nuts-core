# backfill/monitor.py

from .storage import Storage
from .models import BackfillStatus
from typing import Dict

def get_job_progress(storage: Storage, job_id: str) -> Dict[str, float]:
    """
    Returns a dict with total, complete, failed, pending counts and percent_complete.
    """
    total = storage.conn.execute(
        "SELECT COUNT(*) FROM chunks WHERE job_id = ?",
        [job_id]
    ).fetchone()[0]
    complete = storage.conn.execute(
        "SELECT COUNT(*) FROM chunks WHERE job_id = ? AND status = ?",
        [job_id, BackfillStatus.COMPLETE.value]
    ).fetchone()[0]
    failed = storage.conn.execute(
        "SELECT COUNT(*) FROM chunks WHERE job_id = ? AND status = ?",
        [job_id, BackfillStatus.FAILED.value]
    ).fetchone()[0]
    pending = storage.conn.execute(
        "SELECT COUNT(*) FROM chunks WHERE job_id = ? AND status = ?",
        [job_id, BackfillStatus.PENDING.value]
    ).fetchone()[0]
    percent_complete = (complete / total * 100.0) if total > 0 else 0.0
    return {
        "total": total,
        "complete": complete,
        "failed": failed,
        "pending": pending,
        "percent_complete": percent_complete
    }

def format_progress_report(progress: Dict[str, float]) -> str:
    """
    Formats the progress dict into a human-readable string.
    """
    total = progress["total"]
    complete = progress["complete"]
    failed = progress["failed"]
    pending = progress["pending"]
    percent = progress["percent_complete"]
    return f"{complete}/{total} complete, {failed} failed, {pending} pending ({percent}% done)"
