# ============================================
# Patch Date: 2025-07-24T10:55:00Z
# Task: Fix DuckDB CREATE TABLE FROM DataFrame error
# Status: Final
# STRICT PATCH MODE
# ============================================
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

import duckdb
import pandas as pd
import logging
from feature_factory.realtime.deployed_features import apply_all_features

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("FeaturePivotWriter")

def build_features_from_market_data(db_path: str):
    con = duckdb.connect(db_path)
    logger.info(f"🛠️ Connected to DuckDB: {db_path}")

    logger.info("📥 Reading 'market_data' table...")
    df = con.execute("SELECT * FROM market_data").fetchdf()

    if df.empty:
        logger.warning("⚠️ No rows in market_data")
        return

    logger.info(f"✅ Loaded {len(df)} rows — formatting...")
    df = df.rename(columns={"open_time": "timestamp"})
    df["symbol"] = "UNKNOWN"

    logger.info("🚀 Applying features...")
    enriched = apply_all_features(df)

    logger.info("📦 Writing to physical 'features' table...")
    con.execute("DROP TABLE IF EXISTS features")
    con.register("temp_enriched", enriched)
    con.execute("CREATE TABLE features AS SELECT * FROM temp_enriched")

    logger.info(f"✅ Feature table created with {len(enriched)} rows and {len(enriched.columns)} columns.")

if __name__ == "__main__":
    build_features_from_market_data("src/feature_factory/data/features.duckdb")
