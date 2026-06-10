# === PATCHED ===
# Patch Date: 2025-07-25
# Fix: Rename SQL column 'offset' to 'offset_value' to avoid syntax error
# Source: file-MsTgbyzxjqaLmTrmXot1fE
# 🔧 CheckpointService: Persistent Kafka Offset Tracking
# File: src/feature_factory/realtime/checkpoint_service.py
# Purpose: Store and retrieve Kafka consumer offsets in DuckDB for exactly-once resume

import duckdb
import os
from pathlib import Path
from typing import Optional, Tuple

class CheckpointService:
    """
    Manages Kafka consumer offsets saved in DuckDB to allow resuming consumption
    from the last committed position.
    """

    def __init__(self, db_path: str = None):
        # Default to .env DUCKDB_PATH if not provided
        db_file = db_path or os.getenv("DUCKDB_PATH", "data/features.duckdb")
        # Ensure directory exists
        Path(db_file).parent.mkdir(parents=True, exist_ok=True)
        self._con = duckdb.connect(database=db_file)
        # Create offsets table if missing
        self._con.execute(
            """
            CREATE TABLE IF NOT EXISTS kafka_offsets (
                topic TEXT NOT NULL,
                partition INT NOT NULL,
                offset_value BIGINT NOT NULL,
                PRIMARY KEY(topic, partition)
            );
            """
        )

    def get_offset(self, topic: str, partition: int) -> Optional[int]:
        """
        Retrieve the last saved offset for a given topic-partition.
        Returns None if no checkpoint exists.
        """
        row = self._con.execute(
            "SELECT offset_value FROM kafka_offsets WHERE topic = ? AND partition = ?",
            [topic, partition]
        ).fetchone()
        return row[0] if row else None

    def set_offset(self, topic: str, partition: int, offset: int) -> None:
        """
        Save or update the offset for the given topic-partition.
        Uses INSERT OR REPLACE for idempotency.
        """
        self._con.execute(
            "INSERT OR REPLACE INTO kafka_offsets (topic, partition, offset_value) VALUES (?, ?, ?)",
            [topic, partition, offset]
        )
        # Commit isn't strictly needed for DuckDB but included for clarity
        self._con.commit()

# Example integration snippet:
# from checkpoint_service import CheckpointService
# cp = CheckpointService(db_path="data/features.duckdb")
# last = cp.get_offset("raw_ticks", 0)
# consumer.seek(TopicPartition("raw_ticks", 0), last or 0)
# after processing:
# cp.set_offset("raw_ticks", 0, msg.offset + 1)
