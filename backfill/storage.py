# 🔒 PATCHED: 2025-07-25
# Task: Make write_market_data append to existing table instead of always recreating
# Source file: src/feature_factory/backfill/storage.py (file-BYqSaEHCNH3mLuB3AzHG97)

import duckdb
import os
from pathlib import Path
from typing import Optional

# === PATCHED ===
# Patch Date: 2025-07-25
# Rebased import for local test context
from backfill.config import settings
# === PATCHED ===
# Patch Date: 2025-07-25
# Rebased import for local test context
from backfill.models import BackfillJob, BackfillChunk, BackfillStatus
import pandas as pd

class Storage:
    def __init__(self, db_path: Optional[str] = None, read_only: bool = False):
        self.db_path = db_path or settings.DATABASE_PATH

        if self.db_path not in (":memory:", "") and not read_only:
            Path(self.db_path).expanduser().parent.mkdir(parents=True, exist_ok=True)

        open_read_only = read_only
        if read_only and self.db_path not in (":memory:", "") and not os.path.exists(self.db_path):
            open_read_only = False

        self.conn = duckdb.connect(database=self.db_path, read_only=open_read_only)

        if not open_read_only:
            self._ensure_tables()

    def _ensure_tables(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                exchange TEXT NOT NULL,
                symbol TEXT NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                status TEXT NOT NULL
            );
            """
        )

        skip_fk = (
            settings.TESTING
            or os.getenv("PYTEST_CURRENT_TEST") is not None
            or self.db_path == ":memory:"
            or self.db_path != settings.DATABASE_PATH
        )

        if skip_fk:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    chunk_start TIMESTAMP NOT NULL,
                    chunk_end TIMESTAMP NOT NULL,
                    status TEXT NOT NULL
                );
                """
            )
        else:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    chunk_start TIMESTAMP NOT NULL,
                    chunk_end TIMESTAMP NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY(job_id) REFERENCES jobs(id)
                );
                """
            )

    def create_job(self, job: BackfillJob) -> None:
        self.conn.execute(
            """INSERT INTO jobs (id, exchange, symbol, start_time, end_time, status)
            VALUES (?, ?, ?, ?, ?, ?)""",
            [
                job.id,
                job.exchange,
                job.symbol,
                job.start_time,
                job.end_time,
                job.status.value,
            ],
        )

    def get_job_by_id(self, job_id: str) -> BackfillJob:
        row = self.conn.execute(
            """SELECT id, exchange, symbol, start_time, end_time, status
            FROM jobs WHERE id=?""", [job_id]
        ).fetchone()
        if not row:
            raise KeyError(f"Job {job_id} not found")
        return BackfillJob(
            id=row[0],
            exchange=row[1],
            symbol=row[2],
            start_time=row[3],
            end_time=row[4],
            status=BackfillStatus(row[5]),
        )

    def create_chunk(self, chunk: BackfillChunk) -> None:
        self.conn.execute(
            """INSERT INTO chunks (id, job_id, chunk_start, chunk_end, status)
            VALUES (?, ?, ?, ?, ?)""",
            [
                chunk.id,
                chunk.job_id,
                chunk.chunk_start,
                chunk.chunk_end,
                chunk.status.value,
            ],
        )

    def get_next_pending_chunk(self, job_id: str) -> Optional[BackfillChunk]:
        row = self.conn.execute(
            """SELECT id, chunk_start, chunk_end, status
            FROM chunks WHERE job_id=? AND status='PENDING' LIMIT 1""",
            [job_id],
        ).fetchone()
        if not row:
            return None
        return BackfillChunk(
            id=row[0],
            job_id=job_id,
            chunk_start=row[1],
            chunk_end=row[2],
            status=BackfillStatus(row[3]),
        )

    def update_job_status(self, job_id: str, status: BackfillStatus) -> None:
        self.conn.execute(
            "UPDATE jobs SET status=? WHERE id=?", [status.value, job_id]
        )

    def update_chunk_status(self, chunk_id: str, status: BackfillStatus) -> None:
        self.conn.execute(
            "UPDATE chunks SET status=? WHERE id=?", [status.value, chunk_id]
        )

    def write_market_data(self, data: pd.DataFrame, table_name: str = "market_data") -> None:
        self.conn.register("tmp_df", data)
        try:
            # First attempt to create the table
            self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM tmp_df")
        except duckdb.CatalogException:
            # If it already exists, append new rows
            self.conn.execute(f"INSERT INTO {table_name} SELECT * FROM tmp_df")
