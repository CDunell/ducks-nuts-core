# backfill/chunker.py

import uuid
from datetime import timedelta
from .models import BackfillStatus
from .storage import Storage

def generate_chunks(storage: Storage, job_id: str, chunk_hours: int) -> None:
    """
    Slice the job's time range into chunks of chunk_hours hours
    and insert them into the chunks table as PENDING.
    """
    # fetch job details (start_time, end_time)
    job = storage.get_job_by_id(job_id)
    start = job.start_time
    end = job.end_time
    delta = timedelta(hours=chunk_hours)
    current = start
    while current < end:
        chunk_start = current
        chunk_end = min(current + delta, end)
        chunk_id = str(uuid.uuid4())
        storage.conn.execute(
            "INSERT INTO chunks (id, job_id, chunk_start, chunk_end, status) VALUES (?, ?, ?, ?, ?)",
            [chunk_id, job_id, chunk_start, chunk_end, BackfillStatus.PENDING.value],
        )
        current = chunk_end
