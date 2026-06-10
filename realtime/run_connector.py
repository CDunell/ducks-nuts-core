# 🔧 Production-ready real-time runner
# File: src/feature_factory/realtime/run_connector.py

import os
import asyncio
import json
import logging
import signal
from typing import Dict, Any

import pandas as pd

# === PATCHED ===
# Patch date: 2025-07-25
# Task: Fix import to allow execution from CWD (src/feature_factory)
# Source: file-SsmBz2Pc3eYZjejE1HJFjU
# === PATCHED ===
# Patch Date: 2025-07-25
# Replace KafkaConnector with RedisConnector
from realtime.redis_connector import RedisConnector
from realtime.checkpoint_service import CheckpointService
# === PATCHED ===
# Patch Date: 2025-07-25
# Use relative import from inside feature_factory
from backfill.storage import Storage
# === PATCHED ===
# Patch Date: 2025-07-25
# Use relative import from inside feature_factory
from feature_factory import FeatureFactory

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Logging setup
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Configuration
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
CONSUMER_TOPIC = os.getenv("KAFKA_CONSUMER_TOPIC", "raw_ticks")
PRODUCER_TOPIC = os.getenv("KAFKA_PRODUCER_TOPIC", "enriched_features")
GROUP_ID = os.getenv("KAFKA_GROUP_ID", "feature-factory")
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "data/features.duckdb")
FEATURE_TABLE = os.getenv("FEATURE_TABLE", "market_data")
BACKPRESSURE_HIGH = int(os.getenv("BACKPRESSURE_HIGH", 1000))
BACKPRESSURE_LOW = int(os.getenv("BACKPRESSURE_LOW", 100))

# Core components
storage = Storage(db_path=DUCKDB_PATH)
factory = FeatureFactory()
checkpoint = CheckpointService(db_path=DUCKDB_PATH)

# Create connector
connector = RedisConnector()

# Graceful shutdown
def shutdown():
    logger.info("Shutdown signal received, stopping connector...")
    asyncio.create_task(connector.stop())

for sig in (signal.SIGINT, signal.SIGTERM):
    signal.signal(sig, lambda *_: shutdown())

async def message_handler(msg):
    # Deserialize raw message
    raw: Dict[str, Any] = json.loads(msg.value)
    # Compute features
    features = factory.compute_features(raw)
    # Persist to DuckDB
    df = pd.DataFrame([features])
    storage.write_market_data(df, table_name=FEATURE_TABLE)
    # Commit offset
    checkpoint.set_offset(msg.topic, msg.partition, msg.offset + 1)
    # Publish enriched if needed
    if PRODUCER_TOPIC:
        enriched = json.dumps(features).encode()
        await connector.send(enriched)

async def main():
    # Seek to last saved offsets
    await connector.start(message_handler)

if __name__ == "__main__":
    asyncio.run(main())
