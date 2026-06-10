# ============================================
# Patch Date: 2025-07-24T11:00:00Z
# Task: Handle wide-format 'features' table (no pivot)
# Source: features written by apply_all_features()
# STRICT PATCH MODE
# ============================================
import duckdb
import pandas as pd
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SnapshotBuilder")

def build_feature_snapshots(db_path: str):
    logger.info(f"🛠️ Connecting to {db_path}")
    con = duckdb.connect(db_path)

    logger.info("📥 Reading wide-format 'features' table...")
    wide = con.execute("SELECT * FROM features").fetchdf()

    if wide.empty:
        logger.warning("⚠️ No data found in 'features' table.")
        return

    logger.info(f"✅ Loaded {len(wide)} rows — validating format...")
    feature_cols = [col for col in wide.columns if col not in ["timestamp", "symbol"]]
    wide = wide[["timestamp", "symbol"] + sorted(feature_cols)]

    logger.info(f"📦 Writing to materialized table: feature_snapshots ({len(wide)} rows, {len(wide.columns)} columns)...")
    con.execute("DROP TABLE IF EXISTS feature_snapshots")
    con.register("wide", wide)
    con.execute("CREATE TABLE feature_snapshots AS SELECT * FROM wide")

    logger.info("✅ Materialized feature_snapshots table created.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python snapshot_builder.py path/to/features.duckdb")
        sys.exit(1)

    build_feature_snapshots(sys.argv[1])
